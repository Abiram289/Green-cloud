"""
Enhanced VM Placement Algorithms with Load Balancing

This module implements advanced placement algorithms including:
1. Hybrid AI-based placement with multi-objective optimization
2. Load-balancing aware algorithms
3. Comprehensive load balancing metrics
4. Advanced baseline algorithms
"""

import numpy as np
import pandas as pd
import random
import joblib
import json
from typing import Dict, List, Tuple, Optional
from abc import ABC, abstractmethod
import warnings
warnings.filterwarnings('ignore')

class EnhancedPlacementAlgorithm(ABC):
    """Enhanced base class for placement algorithms with load balancing metrics"""
    
    def __init__(self, name: str):
        self.name = name
        self.placement_history = []
        self.load_balancing_metrics = {}
        
    @abstractmethod
    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:
        """Place a VM on the best host according to this algorithm"""
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
    
    def calculate_load_balancing_score(self, hosts: List[Dict], after_placement: Optional[Tuple[int, Dict]] = None) -> Dict:
        """Calculate comprehensive load balancing metrics"""
        cpu_utilizations = []
        ram_utilizations = []
        combined_utilizations = []
        
        for i, host in enumerate(hosts):
            if after_placement and i == after_placement[0]:
                # Use utilization after placement for the selected host
                vm_req = after_placement[1]
                cpu_util = (host["current_cpu_usage"] + vm_req["cpu_required"]) / host["cpu_cores"]
                ram_util = (host["current_ram_usage"] + vm_req["ram_required"]) / host["ram_gb"]
            else:
                cpu_util = host["current_cpu_usage"] / host["cpu_cores"]
                ram_util = host["current_ram_usage"] / host["ram_gb"]
            
            cpu_utilizations.append(cpu_util)
            ram_utilizations.append(ram_util)
            combined_utilizations.append((cpu_util + ram_util) / 2)
        
        # Calculate various load balancing metrics
        cpu_variance = np.var(cpu_utilizations)
        ram_variance = np.var(ram_utilizations)
        combined_variance = np.var(combined_utilizations)
        
        # Load Balancing Index (lower is better balanced)
        cpu_lb_index = np.std(cpu_utilizations) / (np.mean(cpu_utilizations) + 1e-6)
        ram_lb_index = np.std(ram_utilizations) / (np.mean(ram_utilizations) + 1e-6)
        combined_lb_index = np.std(combined_utilizations) / (np.mean(combined_utilizations) + 1e-6)
        
        # Imbalance Degree (Jain's Fairness Index adaptation)
        cpu_sum_sq = sum(u**2 for u in cpu_utilizations)
        ram_sum_sq = sum(u**2 for u in ram_utilizations)
        n_hosts = len(hosts)
        
        cpu_fairness = (sum(cpu_utilizations)**2) / (n_hosts * cpu_sum_sq + 1e-6)
        ram_fairness = (sum(ram_utilizations)**2) / (n_hosts * ram_sum_sq + 1e-6)
        
        # Resource Skewness
        cpu_skewness = max(cpu_utilizations) - min(cpu_utilizations) if cpu_utilizations else 0
        ram_skewness = max(ram_utilizations) - min(ram_utilizations) if ram_utilizations else 0
        
        return {
            'cpu_variance': cpu_variance,
            'ram_variance': ram_variance,
            'combined_variance': combined_variance,
            'cpu_lb_index': cpu_lb_index,
            'ram_lb_index': ram_lb_index,
            'combined_lb_index': combined_lb_index,
            'cpu_fairness': cpu_fairness,
            'ram_fairness': ram_fairness,
            'cpu_skewness': cpu_skewness,
            'ram_skewness': ram_skewness,
            'average_cpu_util': np.mean(cpu_utilizations),
            'average_ram_util': np.mean(ram_utilizations),
            'max_cpu_util': max(cpu_utilizations) if cpu_utilizations else 0,
            'max_ram_util': max(ram_utilizations) if ram_utilizations else 0
        }

class HybridAIPredictorPlacement(EnhancedPlacementAlgorithm):
    """Hybrid AI-based placement with multi-objective optimization and load balancing"""
    
    def __init__(self, model_path: str = "models/hybrid_ai_predictor.pkl"):
        super().__init__("Hybrid-AI")
        try:
            self.hybrid_predictor = joblib.load(model_path)
            self.main_model = self.hybrid_predictor['main_model']
            self.specialized_models = self.hybrid_predictor['specialized_models']
            self.model_weights = self.hybrid_predictor['model_weights']
            
            # Load scaler and metadata
            self.scaler = joblib.load('models/scaler_standard.pkl')
            with open('models/advanced_models_metadata.json', 'r') as f:
                self.metadata = json.load(f)
            self.feature_columns = self.metadata['feature_columns']
            
        except FileNotFoundError:
            print("Hybrid AI model not found, falling back to simple AI predictor")
            self.main_model = joblib.load("models/optimized_random_forest.pkl")
            self.scaler = joblib.load("models/optimized_random_forest_scaler.pkl")
            with open("models/optimized_random_forest_metadata.json", 'r') as f:
                self.metadata = json.load(f)
            self.feature_columns = self.metadata['feature_columns']
            self.specialized_models = {}
            self.model_weights = {}
    
    def prepare_features(self, vm_request: Dict, host: Dict) -> np.ndarray:
        """Prepare features for model prediction with enhanced feature engineering"""
        cpu_util_after, ram_util_after = self.calculate_utilization_after_placement(vm_request, host)
        
        # Base features
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
        }
        
        # Calculate metrics for additional features
        energy_consumption = host["base_power_watts"] * (0.3 + 0.7 * (cpu_util_after ** 1.3))
        usage_cost_factor = 1 + 0.5 * max(cpu_util_after, ram_util_after)
        cost = host["cost_per_hour"] * usage_cost_factor * vm_request.get("expected_runtime_hours", 24)
        sla_violation_risk = host["sla_risk_factor"] + (max(0, cpu_util_after - 0.8) + max(0, ram_util_after - 0.8)) * 0.1
        
        features.update({
            'energy_consumption': energy_consumption,
            'cost': cost,
            'cpu_utilization': cpu_util_after,
            'ram_utilization': ram_util_after,
            'sla_violation_risk': sla_violation_risk,
        })
        
        # Enhanced feature engineering (matching training features)
        features.update({
            'cpu_efficiency_quadratic': (1 - abs(cpu_util_after - 0.7)) ** 2,
            'ram_efficiency_quadratic': (1 - abs(ram_util_after - 0.7)) ** 2,
            'resource_balance_score': 1 - abs(cpu_util_after - ram_util_after),
            'total_utilization': cpu_util_after + ram_util_after,
            'utilization_product': cpu_util_after * ram_util_after,
            'cost_efficiency': cost / (vm_request["cpu_required"] + vm_request["ram_required"]),
            'energy_efficiency': energy_consumption / (host["cpu_cores"] + host["ram_gb"] / 10),
            'cost_energy_ratio': cost / (energy_consumption + 1e-6),
            'host_total_capacity': host["cpu_cores"] + host["ram_gb"] / 10,
            'host_load_density': (features['host_current_cpu_util'] + features['host_current_ram_util']) / 2,
            'remaining_capacity': ((host["cpu_cores"] * (1 - features['host_current_cpu_util'])) + 
                                 (host["ram_gb"] * (1 - features['host_current_ram_util'])) / 10),
            'vm_resource_intensity': vm_request["cpu_required"] * vm_request["ram_required"],
            'vm_total_demand': vm_request["cpu_required"] * vm_request["ram_required"] * vm_request.get("expected_runtime_hours", 24),
            'sla_safety_margin': 1 - sla_violation_risk,
            'cpu_to_ram_ratio': vm_request["cpu_required"] / (vm_request["ram_required"] + 1e-6),
            'host_cpu_to_ram_ratio': host["cpu_cores"] / (host["ram_gb"] + 1e-6),
        })
        
        # Additional derived features
        features['risk_adjusted_efficiency'] = features['resource_balance_score'] * features['sla_safety_margin']
        features['resource_match_score'] = 1 - abs(features['cpu_to_ram_ratio'] - features['host_cpu_to_ram_ratio'])
        
        # Polynomial features
        for base_feature in ['cpu_util_after_placement', 'ram_util_after_placement', 'host_load_density']:
            if base_feature in features:
                features[f'{base_feature}_squared'] = features[base_feature] ** 2
                features[f'{base_feature}_cubed'] = features[base_feature] ** 3
        
        # Create feature vector in correct order
        feature_vector = []
        missing_features = []
        
        for col in self.feature_columns:
            if col in features:
                feature_vector.append(features[col])
            else:
                feature_vector.append(0)  # Default value for missing features
                missing_features.append(col)
        
        # Debug: Print missing features on first run
        if len(missing_features) > 0 and not hasattr(self, '_debug_printed'):
            print(f"DEBUG: Missing {len(missing_features)} features: {missing_features[:10]}...")
            print(f"DEBUG: Available features: {list(features.keys())[:10]}...")
            self._debug_printed = True
        
        return np.array(feature_vector).reshape(1, -1)
    
    def get_multi_objective_scores(self, vm_request: Dict, host: Dict) -> Dict[str, float]:
        """Get scores from specialized models for multi-objective optimization"""
        if not self.specialized_models:
            return {}
        
        features = self.prepare_features(vm_request, host)
        features_scaled = self.scaler.transform(features)
        
        scores = {}
        for objective, model in self.specialized_models.items():
            try:
                prob = model.predict_proba(features_scaled)[0][1]
                scores[objective] = prob
            except:
                scores[objective] = 0.5  # Default neutral score
        
        return scores
    
    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:
        """Place VM using hybrid AI approach with load balancing consideration"""
        feasible_hosts = []
        
        for host in hosts:
            if self.can_place_vm(vm_request, host):
                # Main model prediction
                features = self.prepare_features(vm_request, host)
                features_scaled = self.scaler.transform(features)
                
                try:
                    main_prob = self.main_model.predict_proba(features_scaled)[0][1]
                except:
                    main_prob = 0.5
                
                # Multi-objective scores
                specialized_scores = self.get_multi_objective_scores(vm_request, host)
                
                # Load balancing consideration
                lb_score_before = self.calculate_load_balancing_score(hosts)
                lb_score_after = self.calculate_load_balancing_score(hosts, (host['host_id'], vm_request))
                
                # Load balancing improvement (lower variance is better)
                lb_improvement = (lb_score_before['combined_variance'] - lb_score_after['combined_variance'])
                lb_normalized = 1 / (1 + lb_score_after['combined_lb_index'])  # Normalize to 0-1
                
                # Combine scores
                if specialized_scores:
                    # Weighted combination of specialized scores
                    energy_score = specialized_scores.get('energy_efficient', 0.5)
                    cost_score = specialized_scores.get('cost_efficient', 0.5)
                    balanced_score = specialized_scores.get('balanced', 0.5)
                    
                    combined_specialized = (energy_score + cost_score + balanced_score) / 3
                    
                    # Final score: 50% main model, 30% specialized, 20% load balancing
                    final_score = (0.5 * main_prob + 
                                 0.3 * combined_specialized + 
                                 0.2 * lb_normalized)
                else:
                    # If no specialized models, weight main model and load balancing
                    final_score = 0.7 * main_prob + 0.3 * lb_normalized
                
                feasible_hosts.append({
                    'host_id': host['host_id'],
                    'score': final_score,
                    'main_prob': main_prob,
                    'lb_score': lb_normalized,
                    'specialized_scores': specialized_scores,
                    'host': host
                })
        
        if not feasible_hosts:
            return -1
        
        # Select host with highest combined score
        best_host = max(feasible_hosts, key=lambda x: x['score'])
        return best_host['host_id']

class LoadBalancingFirstFit(EnhancedPlacementAlgorithm):
    """First-Fit with load balancing consideration"""
    
    def __init__(self):
        super().__init__("LB-First-Fit")
    
    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:
        # Sort hosts by current utilization (ascending)
        sorted_hosts = sorted(hosts, key=lambda h: (h["current_cpu_usage"]/h["cpu_cores"] + 
                                                   h["current_ram_usage"]/h["ram_gb"]) / 2)
        
        for host in sorted_hosts:
            if self.can_place_vm(vm_request, host):
                return host["host_id"]
        return -1

class LoadBalancingBestFit(EnhancedPlacementAlgorithm):
    """Best-Fit with load balancing optimization"""
    
    def __init__(self):
        super().__init__("LB-Best-Fit")
    
    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:
        best_host_id = -1
        best_score = -1
        
        for host in hosts:
            if self.can_place_vm(vm_request, host):
                # Calculate utilization after placement
                cpu_util_after = (host["current_cpu_usage"] + vm_request["cpu_required"]) / host["cpu_cores"]
                ram_util_after = (host["current_ram_usage"] + vm_request["ram_required"]) / host["ram_gb"]
                
                # Score based on balanced utilization (prefer hosts that achieve balanced CPU/RAM usage)
                utilization_balance = 1 - abs(cpu_util_after - ram_util_after)
                efficiency_score = 1 - abs((cpu_util_after + ram_util_after) / 2 - 0.7)  # Target 70% utilization
                
                # Remaining resource consideration
                remaining_cpu = host["cpu_cores"] - host["current_cpu_usage"] - vm_request["cpu_required"]
                remaining_ram = host["ram_gb"] - host["current_ram_usage"] - vm_request["ram_required"]
                remaining_normalized = (remaining_cpu / host["cpu_cores"] + remaining_ram / host["ram_gb"]) / 2
                
                # Combined score: balance utilization, efficiency, and resource conservation
                score = 0.4 * utilization_balance + 0.4 * efficiency_score + 0.2 * (1 - remaining_normalized)
                
                if score > best_score:
                    best_score = score
                    best_host_id = host["host_id"]
        
        return best_host_id

class AdaptiveLoadBalancing(EnhancedPlacementAlgorithm):
    """Adaptive algorithm that changes strategy based on system load"""
    
    def __init__(self):
        super().__init__("Adaptive-LB")
        self.load_threshold_low = 0.3
        self.load_threshold_high = 0.7
    
    def place_vm(self, vm_request: Dict, hosts: List[Dict]) -> int:
        # Calculate overall system load
        total_cpu_util = sum(h["current_cpu_usage"]/h["cpu_cores"] for h in hosts) / len(hosts)
        total_ram_util = sum(h["current_ram_usage"]/h["ram_gb"] for h in hosts) / len(hosts)
        system_load = (total_cpu_util + total_ram_util) / 2
        
        if system_load < self.load_threshold_low:
            # Low load: Use best-fit to consolidate
            return self._best_fit_placement(vm_request, hosts)
        elif system_load > self.load_threshold_high:
            # High load: Use load balancing to spread load
            return self._load_balancing_placement(vm_request, hosts)
        else:
            # Medium load: Balanced approach
            return self._balanced_placement(vm_request, hosts)
    
    def _best_fit_placement(self, vm_request: Dict, hosts: List[Dict]) -> int:
        best_host_id = -1
        min_remaining = float('inf')
        
        for host in hosts:
            if self.can_place_vm(vm_request, host):
                remaining_cpu = host["cpu_cores"] - host["current_cpu_usage"] - vm_request["cpu_required"]
                remaining_ram = host["ram_gb"] - host["current_ram_usage"] - vm_request["ram_required"]
                total_remaining = remaining_cpu / host["cpu_cores"] + remaining_ram / host["ram_gb"]
                
                if total_remaining < min_remaining:
                    min_remaining = total_remaining
                    best_host_id = host["host_id"]
        
        return best_host_id
    
    def _load_balancing_placement(self, vm_request: Dict, hosts: List[Dict]) -> int:
        best_host_id = -1
        min_load = float('inf')
        
        for host in hosts:
            if self.can_place_vm(vm_request, host):
                current_load = (host["current_cpu_usage"]/host["cpu_cores"] + 
                               host["current_ram_usage"]/host["ram_gb"]) / 2
                
                if current_load < min_load:
                    min_load = current_load
                    best_host_id = host["host_id"]
        
        return best_host_id
    
    def _balanced_placement(self, vm_request: Dict, hosts: List[Dict]) -> int:
        best_host_id = -1
        best_score = -1
        
        for host in hosts:
            if self.can_place_vm(vm_request, host):
                # Balance between consolidation and load spreading
                cpu_util_after = (host["current_cpu_usage"] + vm_request["cpu_required"]) / host["cpu_cores"]
                ram_util_after = (host["current_ram_usage"] + vm_request["ram_required"]) / host["ram_gb"]
                
                # Efficiency (prefer ~70% utilization)
                avg_util = (cpu_util_after + ram_util_after) / 2
                efficiency = 1 - abs(avg_util - 0.7)
                
                # Balance between CPU and RAM
                balance = 1 - abs(cpu_util_after - ram_util_after)
                
                score = 0.6 * efficiency + 0.4 * balance
                
                if score > best_score:
                    best_score = score
                    best_host_id = host["host_id"]
        
        return best_host_id

class EnhancedMetricsCalculator:
    """Enhanced metrics calculator with load balancing metrics"""
    
    @staticmethod
    def calculate_comprehensive_metrics(hosts: List[Dict], vm_requests: List[Dict], 
                                      placements: List[int], algorithm_name: str) -> Dict:
        """Calculate comprehensive metrics including load balancing"""
        # Standard metrics
        total_energy = 0
        total_cost = 0
        total_cpu_util = 0
        total_ram_util = 0
        sla_violations = 0
        successful_placements = 0
        
        # Load balancing metrics
        cpu_utilizations = []
        ram_utilizations = []
        
        # Host state copy
        host_states = {h['host_id']: h.copy() for h in hosts}
        
        for vm_req, host_id in zip(vm_requests, placements):
            if host_id == -1:
                continue
            
            successful_placements += 1
            host = host_states[host_id]
            
            # Update host state
            host["current_cpu_usage"] += vm_req["cpu_required"]
            host["current_ram_usage"] += vm_req["ram_required"]
            
            # Calculate metrics
            cpu_util = host["current_cpu_usage"] / host["cpu_cores"]
            ram_util = host["current_ram_usage"] / host["ram_gb"]
            
            # Energy and cost
            power_multiplier = 0.3 + 0.7 * (cpu_util ** 1.3)
            energy = host["base_power_watts"] * power_multiplier
            total_energy += energy
            
            usage_cost_factor = 1 + 0.5 * max(cpu_util, ram_util)
            cost = host["cost_per_hour"] * usage_cost_factor * vm_req.get("expected_runtime_hours", 24)
            total_cost += cost
            
            # Utilization
            total_cpu_util += cpu_util
            total_ram_util += ram_util
            
            # SLA violations
            overload_penalty = max(0, cpu_util - 0.8) + max(0, ram_util - 0.8)
            sla_risk = host["sla_risk_factor"] + overload_penalty * 0.1
            if sla_risk > 0.05:
                sla_violations += 1
        
        # Collect final utilizations for load balancing metrics
        for host in host_states.values():
            cpu_utilizations.append(host["current_cpu_usage"] / host["cpu_cores"])
            ram_utilizations.append(host["current_ram_usage"] / host["ram_gb"])
        
        # Calculate load balancing metrics
        cpu_variance = np.var(cpu_utilizations) if cpu_utilizations else 0
        ram_variance = np.var(ram_utilizations) if ram_utilizations else 0
        cpu_std = np.std(cpu_utilizations) if cpu_utilizations else 0
        ram_std = np.std(ram_utilizations) if ram_utilizations else 0
        
        # Load balancing indices
        cpu_mean = np.mean(cpu_utilizations) if cpu_utilizations else 0
        ram_mean = np.mean(ram_utilizations) if ram_utilizations else 0
        
        cpu_lb_index = cpu_std / (cpu_mean + 1e-6) if cpu_mean > 0 else 0
        ram_lb_index = ram_std / (ram_mean + 1e-6) if ram_mean > 0 else 0
        
        # Resource skewness
        cpu_skewness = max(cpu_utilizations) - min(cpu_utilizations) if cpu_utilizations else 0
        ram_skewness = max(ram_utilizations) - min(ram_utilizations) if ram_utilizations else 0
        
        # Jain's Fairness Index
        n_hosts = len(cpu_utilizations)
        if n_hosts > 0:
            cpu_sum = sum(cpu_utilizations)
            cpu_sum_sq = sum(u**2 for u in cpu_utilizations)
            cpu_fairness = (cpu_sum**2) / (n_hosts * cpu_sum_sq + 1e-6) if cpu_sum_sq > 0 else 1
            
            ram_sum = sum(ram_utilizations)
            ram_sum_sq = sum(u**2 for u in ram_utilizations)
            ram_fairness = (ram_sum**2) / (n_hosts * ram_sum_sq + 1e-6) if ram_sum_sq > 0 else 1
        else:
            cpu_fairness = ram_fairness = 1
        
        # Standard aggregated metrics
        if successful_placements > 0:
            avg_cpu_util = total_cpu_util / successful_placements
            avg_ram_util = total_ram_util / successful_placements
        else:
            avg_cpu_util = avg_ram_util = 0
        
        return {
            # Standard metrics
            'total_energy_consumption': total_energy,
            'total_cost': total_cost,
            'average_cpu_utilization': avg_cpu_util,
            'average_ram_utilization': ram_util_after,
            'sla_violations': sla_violations,
            'successful_placements': successful_placements,
            'failed_placements': len(vm_requests) - successful_placements,
            'placement_success_rate': successful_placements / len(vm_requests) if vm_requests else 0,
            
            # Load balancing metrics
            'cpu_variance': cpu_variance,
            'ram_variance': ram_variance,
            'cpu_std_deviation': cpu_std,
            'ram_std_deviation': ram_std,
            'cpu_load_balancing_index': cpu_lb_index,
            'ram_load_balancing_index': ram_lb_index,
            'cpu_skewness': cpu_skewness,
            'ram_skewness': ram_skewness,
            'cpu_fairness_index': cpu_fairness,
            'ram_fairness_index': ram_fairness,
            'combined_load_balance_score': (cpu_lb_index + ram_lb_index) / 2,
            'overall_fairness': (cpu_fairness + ram_fairness) / 2,
            
            # System-wide metrics
            'max_cpu_utilization': max(cpu_utilizations) if cpu_utilizations else 0,
            'min_cpu_utilization': min(cpu_utilizations) if cpu_utilizations else 0,
            'max_ram_utilization': max(ram_utilizations) if ram_utilizations else 0,
            'min_ram_utilization': min(ram_utilizations) if ram_utilizations else 0,
        }

def get_enhanced_algorithms() -> List[EnhancedPlacementAlgorithm]:
    """Get instances of all enhanced placement algorithms"""
    algorithms = [
        HybridAIPredictorPlacement(),
        LoadBalancingFirstFit(),
        LoadBalancingBestFit(),
        AdaptiveLoadBalancing()
    ]
    
    # Add original algorithms for comparison
    from placement_algorithms import (BestFitPlacement, FirstFitPlacement, 
                                    WorstFitPlacement, RandomPlacement, RoundRobinPlacement)
    
    original_algorithms = [
        BestFitPlacement(),
        FirstFitPlacement(), 
        WorstFitPlacement(),
        RandomPlacement(),
        RoundRobinPlacement()
    ]
    
    return algorithms + original_algorithms