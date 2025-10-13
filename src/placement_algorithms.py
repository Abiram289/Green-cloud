"""
VM Placement Algorithms Module

This module implements various VM placement algorithms including:
1. AI-based placement using trained Random Forest model
2. Best-Fit algorithm
3. First-Fit algorithm
4. Random placement
5. Worst-Fit algorithm
6. Round-Robin algorithm
"""

import numpy as np
import pandas as pd
import random
import joblib
import json
from typing import Dict, List, Tuple, Optional
from abc import ABC, abstractmethod

class PlacementAlgorithm(ABC):
    """Abstract base class for placement algorithms"""
    
    def __init__(self, name: str):
        self.name = name
        self.placement_history = []
    
    @abstractmethod
    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:
        """
        Place a VM on the best host according to this algorithm
        
        Args:
            vm_request: VM resource requirements
            hosts: List of available hosts with current state
            
        Returns:
            host_id: ID of selected host (-1 if no suitable host found)
        """
        pass
    
    def can_place_vm(self, vm_request: Dict, host: Dict) -> bool:
        """Check if VM can be placed on host"""
        cpu_after = host["current_cpu_usage"] + vm_request["cpu_required"]
        ram_after = host["current_ram_usage"] + vm_request["ram_required"]
        
        return (cpu_after <= host["cpu_cores"] and 
                ram_after <= host["ram_gb"])
    
    def calculate_utilization_after_placement(self, vm_request: Dict, host: Dict) -> Tuple[float, float]:
        """Calculate CPU and RAM utilization after placing VM"""
        cpu_util = (host["current_cpu_usage"] + vm_request["cpu_required"]) / host["cpu_cores"]
        ram_util = (host["current_ram_usage"] + vm_request["ram_required"]) / host["ram_gb"]
        return cpu_util, ram_util

class AIPredictorPlacement(PlacementAlgorithm):
    """AI-based placement using trained Random Forest model"""
    
    def __init__(self, model_path: str = "models/optimized_random_forest.pkl"):
        super().__init__("AI-Predictor")
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(model_path.replace(".pkl", "_scaler.pkl"))
        
        # Load metadata
        metadata_path = model_path.replace(".pkl", "_metadata.json")
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        self.feature_columns = self.metadata['feature_columns']
    
    def prepare_features(self, vm_request: Dict, host: Dict) -> np.ndarray:
        """Prepare features for model prediction"""
        cpu_util_after, ram_util_after = self.calculate_utilization_after_placement(vm_request, host)
        
        # Calculate features matching those used in training
        features = {
            'vm_cpu_required': vm_request["cpu_required"],
            'vm_ram_required': vm_request["ram_required"],
            'vm_runtime_hours': vm_request.get("expected_runtime_hours", 24),
            'vm_sla_requirement': vm_request.get("sla_requirement", 0.99),
            'vm_priority_low': 1 if vm_request.get("priority", "medium") == "low" else 0,
            'vm_priority_medium': 1 if vm_request.get("priority", "medium") == "medium" else 0,
            'vm_priority_high': 1 if vm_request.get("priority", "medium") == "high" else 0,
            
            'host_id': host["host_id"],
            'host_cpu_cores': host["cpu_cores"],
            'host_ram_gb': host["ram_gb"],
            'host_base_power': host["base_power_watts"],
            'host_cost_per_hour': host["cost_per_hour"],
            'host_current_cpu_util': host["current_cpu_usage"] / host["cpu_cores"],
            'host_current_ram_util': host["current_ram_usage"] / host["ram_gb"],
            'host_sla_risk': host["sla_risk_factor"],
            
            'cpu_util_after_placement': cpu_util_after,
            'ram_util_after_placement': ram_util_after,
            'available_cpu_ratio': (host["cpu_cores"] - host["current_cpu_usage"]) / vm_request["cpu_required"],
            'available_ram_ratio': (host["ram_gb"] - host["current_ram_usage"]) / vm_request["ram_required"],
            
            # Calculate additional metrics for engineered features
            'energy_consumption': host["base_power_watts"] * (0.3 + 0.7 * (cpu_util_after ** 1.3)),
            'cost': host["cost_per_hour"] * (1 + 0.5 * max(cpu_util_after, ram_util_after)) * vm_request.get("expected_runtime_hours", 24),
            'cpu_utilization': cpu_util_after,
            'ram_utilization': ram_util_after,
            'sla_violation_risk': host["sla_risk_factor"] + (max(0, cpu_util_after - 0.8) + max(0, ram_util_after - 0.8)) * 0.1,
        }
        
        # Add engineered features
        features.update({
            'cpu_efficiency_score': 1 - abs(cpu_util_after - 0.7),
            'ram_efficiency_score': 1 - abs(ram_util_after - 0.7),
            'total_available_resources': (host["cpu_cores"] * (1 - features['host_current_cpu_util']) + 
                                        host["ram_gb"] * (1 - features['host_current_ram_util']) / 10),
            'cost_per_cpu': features['cost'] / (vm_request["cpu_required"] * vm_request.get("expected_runtime_hours", 24)),
            'cost_per_ram': features['cost'] / (vm_request["ram_required"] * vm_request.get("expected_runtime_hours", 24)),
            'power_per_cpu': features['energy_consumption'] / host["cpu_cores"],
            'total_sla_risk': features['host_sla_risk'] + features['sla_violation_risk'],
            'utilization_balance': abs(cpu_util_after - ram_util_after),
            'vm_complexity': vm_request["cpu_required"] * vm_request["ram_required"] * vm_request.get("sla_requirement", 0.99),
        })
        
        # Create feature vector in the correct order
        feature_vector = [features.get(col, 0) for col in self.feature_columns]
        return np.array(feature_vector).reshape(1, -1)
    
    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:
        """Place VM using AI model prediction"""
        feasible_hosts = []
        
        for host in hosts:
            if self.can_place_vm(vm_request, host):
                # Prepare features for prediction
                features = self.prepare_features(vm_request, host)
                features_scaled = self.scaler.transform(features)
                
                # Get prediction probability
                prob = self.model.predict_proba(features_scaled)[0][1]  # Probability of being optimal
                
                feasible_hosts.append({
                    'host_id': host['host_id'],
                    'probability': prob,
                    'host': host
                })
        
        if not feasible_hosts:
            return -1  # No feasible hosts
        
        # Select host with highest probability of being optimal
        best_host = max(feasible_hosts, key=lambda x: x['probability'])
        return best_host['host_id']

class BestFitPlacement:

    """Best-Fit placement algorithm"""

    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:

        best_host = -1

        min_remaining_capacity = float('inf')

        

        for i, host in enumerate(hosts):

            if (host['current_cpu_usage'] + vm_request['cpu_required'] <= host['cpu_cores'] and

                host['current_ram_usage'] + vm_request['ram_required'] <= host['ram_gb']):

                

                remaining_cpu = host['cpu_cores'] - (host['current_cpu_usage'] + vm_request['cpu_required'])

                remaining_ram = host['ram_gb'] - (host['current_ram_usage'] + vm_request['ram_required'])

                remaining_capacity = remaining_cpu + remaining_ram

                

                if remaining_capacity < min_remaining_capacity:

                    min_remaining_capacity = remaining_capacity

                    best_host = i

        

        return best_host



class FirstFitPlacement:

    """First-Fit placement algorithm"""

    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:

        for i, host in enumerate(hosts):

            if (host['current_cpu_usage'] + vm_request['cpu_required'] <= host['cpu_cores'] and

                host['current_ram_usage'] + vm_request['ram_required'] <= host['ram_gb']):

                return i

        return -1



class WorstFitPlacement:

    """Worst-Fit placement algorithm"""

    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:

        worst_host = -1

        max_remaining_capacity = -1

        

        for i, host in enumerate(hosts):

            if (host['current_cpu_usage'] + vm_request['cpu_required'] <= host['cpu_cores'] and

                host['current_ram_usage'] + vm_request['ram_required'] <= host['ram_gb']):

                

                remaining_cpu = host['cpu_cores'] - (host['current_cpu_usage'] + vm_request['cpu_required'])

                remaining_ram = host['ram_gb'] - (host['current_ram_usage'] + vm_request['ram_required'])

                remaining_capacity = remaining_cpu + remaining_ram

                

                if remaining_capacity > max_remaining_capacity:

                    max_remaining_capacity = remaining_capacity

                    worst_host = i

        

        return worst_host



class RandomPlacement:

    """Random placement algorithm"""

    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:

        feasible_hosts = []

        for i, host in enumerate(hosts):

            if (host['current_cpu_usage'] + vm_request['cpu_required'] <= host['cpu_cores'] and

                host['current_ram_usage'] + vm_request['ram_required'] <= host['ram_gb']):

                feasible_hosts.append(i)

        

        if feasible_hosts:

            return random.choice(feasible_hosts)

        return -1



class RoundRobinPlacement:

    """Round-Robin placement algorithm"""

    def __init__(self):

        self.next_host = 0

        

    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:

        for i in range(len(hosts)):

            host_idx = (self.next_host + i) % len(hosts)

            host = hosts[host_idx]

            

            if (host['current_cpu_usage'] + vm_request['cpu_required'] <= host['cpu_cores'] and

                host['current_ram_usage'] + vm_request['ram_required'] <= host['ram_gb']):

                self.next_host = (host_idx + 1) % len(hosts)

                return host_idx

        

        return -1

class PlacementMetricsCalculator:
    """Calculate placement metrics for evaluation"""
    
    @staticmethod
    def calculate_metrics(hosts: List[Dict], vm_requests: List[Dict], placements: List[int]) -> Dict:
        """Calculate comprehensive metrics for a set of placements"""
        total_energy = 0
        total_cost = 0
        total_cpu_util = 0
        total_ram_util = 0
        sla_violations = 0
        successful_placements = 0
        
        # Create host state copy for calculations
        host_states = {h['host_id']: h.copy() for h in hosts}
        
        for vm_req, host_id in zip(vm_requests, placements):
            if host_id == -1:  # Failed placement
                continue
            
            successful_placements += 1
            host = host_states[host_id]
            
            # Update host state after placement
            host["current_cpu_usage"] += vm_req["cpu_required"]
            host["current_ram_usage"] += vm_req["ram_required"]
            
            # Calculate metrics
            cpu_util = host["current_cpu_usage"] / host["cpu_cores"]
            ram_util = host["current_ram_usage"] / host["ram_gb"]
            
            # Energy consumption (non-linear with utilization)
            power_multiplier = 0.3 + 0.7 * (cpu_util ** 1.3)
            energy = host["base_power_watts"] * power_multiplier
            total_energy += energy
            
            # Cost calculation
            usage_cost_factor = 1 + 0.5 * max(cpu_util, ram_util)
            cost = host["cost_per_hour"] * usage_cost_factor * vm_req.get("expected_runtime_hours", 24)
            total_cost += cost
            
            # Utilization
            total_cpu_util += cpu_util
            total_ram_util += ram_util
            
            # SLA violations (high utilization increases risk)
            overload_penalty = max(0, cpu_util - 0.8) + max(0, ram_util - 0.8)
            sla_risk = host["sla_risk_factor"] + overload_penalty * 0.1
            if sla_risk > 0.05:  # Threshold for SLA violation
                sla_violations += 1
        
        # Aggregate metrics
        if successful_placements > 0:
            avg_cpu_util = total_cpu_util / successful_placements
            avg_ram_util = total_ram_util / successful_placements
        else:
            avg_cpu_util = avg_ram_util = 0
        
        return {
            'total_energy_consumption': total_energy,
            'total_cost': total_cost,
            'average_cpu_utilization': avg_cpu_util,
            'average_ram_utilization': avg_ram_util,
            'sla_violations': sla_violations,
            'successful_placements': successful_placements,
            'failed_placements': len(vm_requests) - successful_placements,
            'placement_success_rate': successful_placements / len(vm_requests) if vm_requests else 0
        }

def get_all_algorithms() -> List[PlacementAlgorithm]:
    """Get instances of all placement algorithms"""
    return [
        AIPredictorPlacement(),
        BestFitPlacement(),
        FirstFitPlacement(),
        WorstFitPlacement(),
        RandomPlacement(),
        RoundRobinPlacement()
    ]