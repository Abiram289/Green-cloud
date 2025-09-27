"""
VM Placement Optimization - Data Generation Module

This module generates synthetic data for VM placement optimization,
focusing on 5 key metrics:
1. Energy Consumption
2. Cost (OPEX)
3. CPU Utilization
4. RAM Utilization
5. SLA Violations
"""

import numpy as np
import pandas as pd
import random
from typing import List, Dict, Tuple
import json

class DataGenerator:
    def __init__(self, num_hosts=20, num_scenarios=2000, seed=42):
        """
        Initialize the data generator
        
        Args:
            num_hosts: Number of physical hosts in the datacenter
            num_scenarios: Number of VM placement scenarios to generate
            seed: Random seed for reproducibility
        """
        self.num_hosts = num_hosts
        self.num_scenarios = num_scenarios
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
        
        # Host specifications (varied to simulate real datacenter)
        self.host_specs = self._generate_host_specifications()
        
    def _generate_host_specifications(self) -> List[Dict]:
        """Generate diverse host specifications"""
        host_types = [
            {"cpu_cores": 16, "ram_gb": 64, "base_power_watts": 200, "cost_per_hour": 0.8},
            {"cpu_cores": 32, "ram_gb": 128, "base_power_watts": 350, "cost_per_hour": 1.5},
            {"cpu_cores": 64, "ram_gb": 256, "base_power_watts": 500, "cost_per_hour": 2.2},
            {"cpu_cores": 8, "ram_gb": 32, "base_power_watts": 120, "cost_per_hour": 0.5},
        ]
        
        hosts = []
        for i in range(self.num_hosts):
            # Select host type with some variation
            base_type = random.choice(host_types)
            
            # Add some variation to specifications
            variation = 0.9 + np.random.random() * 0.2  # ±10% variation
            
            host = {
                "host_id": i,
                "cpu_cores": int(base_type["cpu_cores"] * variation),
                "ram_gb": int(base_type["ram_gb"] * variation),
                "base_power_watts": base_type["base_power_watts"] * variation,
                "cost_per_hour": base_type["cost_per_hour"] * variation,
                # Dynamic variables (will change with load)
                "current_cpu_usage": 0.0,
                "current_ram_usage": 0.0,
                "current_power_watts": 0.0,
                "sla_risk_factor": np.random.uniform(0.01, 0.05),  # Base SLA risk
            }
            hosts.append(host)
        
        return hosts
    
    def _generate_vm_request(self) -> Dict:
        """Generate a single VM request"""
        # VM types with different resource requirements
        vm_types = [
            {"cpu": 1, "ram": 2, "type": "micro", "sla_requirement": 0.99},
            {"cpu": 2, "ram": 4, "type": "small", "sla_requirement": 0.995},
            {"cpu": 4, "ram": 8, "type": "medium", "sla_requirement": 0.99},
            {"cpu": 8, "ram": 16, "type": "large", "sla_requirement": 0.999},
            {"cpu": 16, "ram": 32, "type": "xlarge", "sla_requirement": 0.9995},
        ]
        
        vm_type = random.choice(vm_types)
        
        # Add some variation to requirements
        cpu_variation = 0.8 + np.random.random() * 0.4  # ±20% variation
        ram_variation = 0.8 + np.random.random() * 0.4
        
        return {
            "vm_id": f"vm_{np.random.randint(10000, 99999)}",
            "cpu_required": max(1, int(vm_type["cpu"] * cpu_variation)),
            "ram_required": max(1, int(vm_type["ram"] * ram_variation)),
            "vm_type": vm_type["type"],
            "sla_requirement": vm_type["sla_requirement"],
            "expected_runtime_hours": np.random.exponential(24),  # Average 24 hours
            "priority": np.random.choice(["low", "medium", "high"], p=[0.5, 0.3, 0.2])
        }
    
    def _calculate_host_metrics(self, host: Dict, vm_request: Dict) -> Dict:
        """Calculate metrics if VM is placed on this host"""
        # Calculate new utilization after placing VM
        new_cpu_util = (host["current_cpu_usage"] + vm_request["cpu_required"]) / host["cpu_cores"]
        new_ram_util = (host["current_ram_usage"] + vm_request["ram_required"]) / host["ram_gb"]
        
        # Energy consumption calculation (non-linear with utilization)
        cpu_load_factor = new_cpu_util
        power_multiplier = 0.3 + 0.7 * (cpu_load_factor ** 1.3)  # Non-linear power scaling
        energy_consumption = host["base_power_watts"] * power_multiplier
        
        # Cost calculation (includes base cost + usage cost)
        usage_cost_factor = 1 + 0.5 * max(new_cpu_util, new_ram_util)  # Higher usage = higher cost
        total_cost = host["cost_per_hour"] * usage_cost_factor * vm_request["expected_runtime_hours"]
        
        # SLA violation risk calculation
        overload_penalty = 0
        if new_cpu_util > 0.8:  # High CPU utilization increases risk
            overload_penalty += (new_cpu_util - 0.8) * 0.1
        if new_ram_util > 0.8:  # High RAM utilization increases risk
            overload_penalty += (new_ram_util - 0.8) * 0.1
        
        sla_violation_risk = host["sla_risk_factor"] + overload_penalty
        sla_compliance = max(0, 1 - sla_violation_risk)
        
        # Check if placement is feasible
        feasible = (new_cpu_util <= 1.0 and new_ram_util <= 1.0)
        
        return {
            "host_id": host["host_id"],
            "feasible": feasible,
            "energy_consumption": energy_consumption,
            "cost": total_cost,
            "cpu_utilization": new_cpu_util,
            "ram_utilization": new_ram_util,
            "sla_violation_risk": sla_violation_risk,
            "sla_compliance": sla_compliance,
            "new_cpu_util": new_cpu_util,
            "new_ram_util": new_ram_util
        }
    
    def _calculate_composite_score(self, metrics: Dict, weights: Dict = None) -> float:
        """Calculate composite optimization score"""
        if weights is None:
            # Default weights for multi-objective optimization
            weights = {
                "energy": 0.2,
                "cost": 0.25,
                "cpu_efficiency": 0.2,
                "ram_efficiency": 0.2,
                "sla_compliance": 0.15
            }
        
        if not metrics["feasible"]:
            return float('inf')  # Infeasible placements get worst score
        
        # Normalize metrics (lower is better for most, higher for efficiency/compliance)
        energy_score = metrics["energy_consumption"] / 1000  # Normalize to reasonable scale
        cost_score = metrics["cost"] / 100  # Normalize to reasonable scale
        
        # For utilization: we want balanced utilization (not too low, not too high)
        # Optimal utilization is around 70%
        cpu_eff_score = abs(metrics["cpu_utilization"] - 0.7) * 2  # Penalty for deviation from 70%
        ram_eff_score = abs(metrics["ram_utilization"] - 0.7) * 2
        
        sla_score = 1 - metrics["sla_compliance"]  # Lower violation risk is better
        
        # Weighted composite score (lower is better)
        composite_score = (
            weights["energy"] * energy_score +
            weights["cost"] * cost_score +
            weights["cpu_efficiency"] * cpu_eff_score +
            weights["ram_efficiency"] * ram_eff_score +
            weights["sla_compliance"] * sla_score
        )
        
        return composite_score
    
    def generate_scenario(self) -> Dict:
        """Generate a single VM placement scenario"""
        vm_request = self._generate_vm_request()
        
        # Calculate metrics for each host
        host_metrics = []
        for host in self.host_specs:
            metrics = self._calculate_host_metrics(host, vm_request)
            metrics["composite_score"] = self._calculate_composite_score(metrics)
            host_metrics.append(metrics)
        
        # Find the best host (lowest composite score among feasible options)
        feasible_hosts = [m for m in host_metrics if m["feasible"]]
        if feasible_hosts:
            best_host = min(feasible_hosts, key=lambda x: x["composite_score"])
            optimal_host_id = best_host["host_id"]
        else:
            # If no feasible hosts, choose the least bad option
            optimal_host_id = min(host_metrics, key=lambda x: x["composite_score"])["host_id"]
        
        return {
            "vm_request": vm_request,
            "host_metrics": host_metrics,
            "optimal_host_id": optimal_host_id
        }
    
    def generate_dataset(self) -> pd.DataFrame:
        """Generate complete dataset for training"""
        print(f"Generating {self.num_scenarios} VM placement scenarios...")
        
        data = []
        for scenario_id in range(self.num_scenarios):
            if scenario_id % 200 == 0:
                print(f"Progress: {scenario_id}/{self.num_scenarios}")
            
            scenario = self.generate_scenario()
            vm_req = scenario["vm_request"]
            
            # Create training samples: one for each host
            for host_metrics in scenario["host_metrics"]:
                if host_metrics["feasible"]:  # Only include feasible placements
                    sample = {
                        # VM features
                        "vm_cpu_required": vm_req["cpu_required"],
                        "vm_ram_required": vm_req["ram_required"],
                        "vm_runtime_hours": vm_req["expected_runtime_hours"],
                        "vm_sla_requirement": vm_req["sla_requirement"],
                        "vm_priority_low": 1 if vm_req["priority"] == "low" else 0,
                        "vm_priority_medium": 1 if vm_req["priority"] == "medium" else 0,
                        "vm_priority_high": 1 if vm_req["priority"] == "high" else 0,
                        
                        # Host features
                        "host_id": host_metrics["host_id"],
                        "host_cpu_cores": self.host_specs[host_metrics["host_id"]]["cpu_cores"],
                        "host_ram_gb": self.host_specs[host_metrics["host_id"]]["ram_gb"],
                        "host_base_power": self.host_specs[host_metrics["host_id"]]["base_power_watts"],
                        "host_cost_per_hour": self.host_specs[host_metrics["host_id"]]["cost_per_hour"],
                        "host_current_cpu_util": self.host_specs[host_metrics["host_id"]]["current_cpu_usage"] / self.host_specs[host_metrics["host_id"]]["cpu_cores"],
                        "host_current_ram_util": self.host_specs[host_metrics["host_id"]]["current_ram_usage"] / self.host_specs[host_metrics["host_id"]]["ram_gb"],
                        "host_sla_risk": self.host_specs[host_metrics["host_id"]]["sla_risk_factor"],
                        
                        # Derived features
                        "cpu_util_after_placement": host_metrics["cpu_utilization"],
                        "ram_util_after_placement": host_metrics["ram_utilization"],
                        "available_cpu_ratio": (self.host_specs[host_metrics["host_id"]]["cpu_cores"] - self.host_specs[host_metrics["host_id"]]["current_cpu_usage"]) / vm_req["cpu_required"],
                        "available_ram_ratio": (self.host_specs[host_metrics["host_id"]]["ram_gb"] - self.host_specs[host_metrics["host_id"]]["current_ram_usage"]) / vm_req["ram_required"],
                        
                        # Target metrics (what we're trying to optimize)
                        "energy_consumption": host_metrics["energy_consumption"],
                        "cost": host_metrics["cost"],
                        "cpu_utilization": host_metrics["cpu_utilization"],
                        "ram_utilization": host_metrics["ram_utilization"],
                        "sla_violation_risk": host_metrics["sla_violation_risk"],
                        "composite_score": host_metrics["composite_score"],
                        
                        # Label: 1 if this is the optimal host, 0 otherwise
                        "is_optimal": 1 if host_metrics["host_id"] == scenario["optimal_host_id"] else 0
                    }
                    data.append(sample)
            
            # Simulate dynamic changes in host utilization
            if scenario_id % 50 == 0:  # Update host state every 50 scenarios
                self._update_host_utilization()
        
        print(f"Generated {len(data)} training samples")
        return pd.DataFrame(data)
    
    def _update_host_utilization(self):
        """Simulate changes in host utilization over time"""
        for host in self.host_specs:
            # Simulate some VMs being terminated and new ones being added
            cpu_change = np.random.normal(0, 0.1)  # Small random changes
            ram_change = np.random.normal(0, 0.1)
            
            host["current_cpu_usage"] = max(0, min(host["cpu_cores"] * 0.9, 
                                                  host["current_cpu_usage"] + cpu_change * host["cpu_cores"]))
            host["current_ram_usage"] = max(0, min(host["ram_gb"] * 0.9,
                                                  host["current_ram_usage"] + ram_change * host["ram_gb"]))
    
    def save_dataset(self, filename: str = "vm_placement_dataset.csv"):
        """Generate and save the dataset"""
        df = self.generate_dataset()
        filepath = f"data/{filename}"
        df.to_csv(filepath, index=False)
        print(f"Dataset saved to {filepath}")
        
        # Save host specifications
        with open("data/host_specifications.json", "w") as f:
            json.dump(self.host_specs, f, indent=2)
        
        # Print dataset statistics
        print(f"\nDataset Statistics:")
        print(f"Total samples: {len(df)}")
        print(f"Optimal placements: {df['is_optimal'].sum()}")
        print(f"Features: {len(df.columns) - 1}")  # -1 for target column
        print(f"Unique VMs: {len(df[['vm_cpu_required', 'vm_ram_required']].drop_duplicates())}")
        print(f"Unique hosts: {df['host_id'].nunique()}")
        
        return df

if __name__ == "__main__":
    # Generate dataset
    generator = DataGenerator(num_hosts=20, num_scenarios=2000)
    dataset = generator.save_dataset()
    
    print("\nSample data:")
    print(dataset.head())
    
    print("\nFeature correlation with optimal placement:")
    correlations = dataset.select_dtypes(include=[np.number]).corrwith(dataset['is_optimal']).sort_values(key=abs, ascending=False)
    print(correlations)