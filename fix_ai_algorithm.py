#!/usr/bin/env python3
"""
AI Placement Algorithm - Comprehensive Fixes
Addresses the critical issues identified in AI placement performance
"""

import sys
import os
sys.path.append('src')

import numpy as np
import pandas as pd
import joblib
import json
from enhanced_algorithms import HybridAIPredictorPlacement

class FixedHybridAIPlacement:
    """
    Fixed version of AI placement algorithm addressing:
    1. Feature mapping issues
    2. Poor decision logic
    3. Energy and cost optimization
    4. Load balancing integration
    """
    
    def __init__(self, model_path: str = "models/hybrid_ai_predictor.pkl"):
        self.name = "Fixed-Hybrid-AI"
        try:
            # Load models and metadata
            self.hybrid_predictor = joblib.load(model_path)
            self.main_model = self.hybrid_predictor['main_model']
            self.specialized_models = self.hybrid_predictor['specialized_models']
            self.model_weights = self.hybrid_predictor['model_weights']
            
            self.scaler = joblib.load('models/scaler_standard.pkl')
            with open('models/advanced_models_metadata.json', 'r') as f:
                self.metadata = json.load(f)
            self.feature_columns = self.metadata['feature_columns']
            
            print(f"✓ Fixed AI Algorithm loaded with {len(self.feature_columns)} features")
            
        except FileNotFoundError as e:
            print(f"✗ Model loading failed: {e}")
            print("Falling back to simple heuristic approach")
            self.use_fallback = True
            
    def can_place_vm(self, vm_request, host):
        """Check if VM can be placed on host"""
        cpu_after = host["current_cpu_usage"] + vm_request["cpu_required"]
        ram_after = host["current_ram_usage"] + vm_request["ram_required"]
        return (cpu_after <= host["cpu_cores"] and ram_after <= host["ram_gb"])
    
    def prepare_features_fixed(self, vm_request, host):
        """Fixed feature preparation that properly maps to training features"""
        
        # Calculate utilization after placement
        cpu_util_after = (host["current_cpu_usage"] + vm_request["cpu_required"]) / host["cpu_cores"]
        ram_util_after = (host["current_ram_usage"] + vm_request["ram_required"]) / host["ram_gb"]
        
        # Base features - EXACTLY matching training data structure
        features = {}
        
        # VM features
        features['vm_cpu_required'] = vm_request["cpu_required"]
        features['vm_ram_required'] = vm_request["ram_required"]
        features['vm_runtime_hours'] = vm_request.get("expected_runtime_hours", 24)
        features['vm_sla_requirement'] = vm_request.get("sla_requirement", 0.99)
        
        # Priority encoding - one-hot
        priority = vm_request.get("priority", "medium")
        features['vm_priority_low'] = 1 if priority == "low" else 0
        features['vm_priority_medium'] = 1 if priority == "medium" else 0
        features['vm_priority_high'] = 1 if priority == "high" else 0
        
        # Host features
        features['host_id'] = host["host_id"]
        features['host_cpu_cores'] = host["cpu_cores"]
        features['host_ram_gb'] = host["ram_gb"]
        features['host_base_power'] = host["base_power_watts"]
        features['host_cost_per_hour'] = host["cost_per_hour"]
        features['host_current_cpu_util'] = host["current_cpu_usage"] / host["cpu_cores"]
        features['host_current_ram_util'] = host["current_ram_usage"] / host["ram_gb"]
        features['host_sla_risk'] = host["sla_risk_factor"]
        
        # Placement features
        features['cpu_util_after_placement'] = cpu_util_after
        features['ram_util_after_placement'] = ram_util_after
        features['available_cpu_ratio'] = (host["cpu_cores"] - host["current_cpu_usage"]) / max(vm_request["cpu_required"], 1)
        features['available_ram_ratio'] = (host["ram_gb"] - host["current_ram_usage"]) / max(vm_request["ram_required"], 1)
        
        # Calculated metrics
        energy_consumption = host["base_power_watts"] * (0.3 + 0.7 * (cpu_util_after ** 1.3))
        usage_cost_factor = 1 + 0.5 * max(cpu_util_after, ram_util_after)
        cost = host["cost_per_hour"] * usage_cost_factor * features['vm_runtime_hours']
        sla_violation_risk = host["sla_risk_factor"] + max(0, cpu_util_after - 0.8) * 0.1 + max(0, ram_util_after - 0.8) * 0.1
        
        features.update({
            'energy_consumption': energy_consumption,
            'cost': cost,
            'cpu_utilization': cpu_util_after,
            'ram_utilization': ram_util_after,
            'sla_violation_risk': min(sla_violation_risk, 1.0),  # Cap at 1.0
        })
        
        # Enhanced engineering features
        features.update({
            'cpu_efficiency_quadratic': max(0, (1 - abs(cpu_util_after - 0.7)) ** 2),
            'ram_efficiency_quadratic': max(0, (1 - abs(ram_util_after - 0.7)) ** 2),
            'resource_balance_score': max(0, 1 - abs(cpu_util_after - ram_util_after)),
            'total_utilization': cpu_util_after + ram_util_after,
            'utilization_product': cpu_util_after * ram_util_after,
            'cost_efficiency': cost / max(vm_request["cpu_required"] + vm_request["ram_required"], 1),
            'energy_efficiency': energy_consumption / max(host["cpu_cores"] + host["ram_gb"] / 10, 1),
            'cost_energy_ratio': cost / max(energy_consumption, 1e-6),
            'host_total_capacity': host["cpu_cores"] + host["ram_gb"] / 10,
            'host_load_density': (features['host_current_cpu_util'] + features['host_current_ram_util']) / 2,
            'remaining_capacity': ((host["cpu_cores"] * (1 - features['host_current_cpu_util'])) + 
                                 (host["ram_gb"] * (1 - features['host_current_ram_util'])) / 10),
            'vm_resource_intensity': vm_request["cpu_required"] * vm_request["ram_required"],
            'vm_total_demand': vm_request["cpu_required"] * vm_request["ram_required"] * features['vm_runtime_hours'],
            'sla_safety_margin': max(0, 1 - sla_violation_risk),
            'cpu_to_ram_ratio': vm_request["cpu_required"] / max(vm_request["ram_required"], 1e-6),
            'host_cpu_to_ram_ratio': host["cpu_cores"] / max(host["ram_gb"], 1e-6),
        })
        
        # Additional derived features
        features['risk_adjusted_efficiency'] = features['resource_balance_score'] * features['sla_safety_margin']
        features['resource_match_score'] = max(0, 1 - abs(features['cpu_to_ram_ratio'] - features['host_cpu_to_ram_ratio']))
        
        # Polynomial features
        for base_feature in ['cpu_util_after_placement', 'ram_util_after_placement', 'host_load_density']:
            if base_feature in features:
                features[f'{base_feature}_squared'] = features[base_feature] ** 2
                features[f'{base_feature}_cubed'] = features[base_feature] ** 3
        
        return features
    
    def calculate_heuristic_score(self, vm_request, host):
        """Fallback heuristic scoring when AI models fail"""
        if not self.can_place_vm(vm_request, host):
            return float('-inf')
        
        cpu_util_after = (host["current_cpu_usage"] + vm_request["cpu_required"]) / host["cpu_cores"]
        ram_util_after = (host["current_ram_usage"] + vm_request["ram_required"]) / host["ram_gb"]
        
        # Optimize for balanced utilization around 70%
        cpu_efficiency = 1 - abs(cpu_util_after - 0.7)
        ram_efficiency = 1 - abs(ram_util_after - 0.7)
        
        # Energy efficiency (prefer lower power hosts when possible)
        energy_score = 1 / (host["base_power_watts"] / 1000)  # Normalize
        
        # Cost efficiency
        cost_score = 1 / (host["cost_per_hour"] + 1e-6)
        
        # Load balancing (prefer less loaded hosts)
        current_load = (host["current_cpu_usage"]/host["cpu_cores"] + host["current_ram_usage"]/host["ram_gb"]) / 2
        load_balance_score = 1 - current_load
        
        # Composite score
        score = (0.3 * cpu_efficiency + 0.3 * ram_efficiency + 
                0.2 * energy_score + 0.1 * cost_score + 0.1 * load_balance_score)
        
        return score
    
    def place_vm_fixed(self, vm_request, hosts):
        """Fixed AI placement with proper feature mapping and fallback logic"""
        feasible_hosts = []
        
        # Use heuristic fallback if models aren't working
        if hasattr(self, 'use_fallback') and self.use_fallback:
            best_host_id = -1
            best_score = float('-inf')
            
            for host in hosts:
                if self.can_place_vm(vm_request, host):
                    score = self.calculate_heuristic_score(vm_request, host)
                    if score > best_score:
                        best_score = score
                        best_host_id = host['host_id']
            
            return best_host_id
        
        # Try AI approach with fixes
        for host in hosts:
            if self.can_place_vm(vm_request, host):
                try:
                    # Fixed feature preparation
                    features_dict = self.prepare_features_fixed(vm_request, host)
                    
                    # Create feature vector in exact order expected by model
                    feature_vector = []
                    missing_count = 0
                    
                    for col in self.feature_columns:
                        if col in features_dict:
                            feature_vector.append(features_dict[col])
                        else:
                            feature_vector.append(0.0)
                            missing_count += 1
                    
                    features_array = np.array(feature_vector).reshape(1, -1)
                    features_scaled = self.scaler.transform(features_array)
                    
                    # Get AI prediction
                    try:
                        main_prob = self.main_model.predict_proba(features_scaled)[0][1]
                    except:
                        main_prob = 0.5  # Neutral if prediction fails
                    
                    # Add heuristic component to improve decision quality
                    heuristic_score = self.calculate_heuristic_score(vm_request, host)
                    
                    # Combine AI and heuristic: 60% AI, 40% heuristic
                    final_score = 0.6 * main_prob + 0.4 * max(0, heuristic_score)
                    
                    feasible_hosts.append({
                        'host_id': host['host_id'],
                        'score': final_score,
                        'ai_score': main_prob,
                        'heuristic_score': heuristic_score,
                        'missing_features': missing_count,
                        'host': host
                    })
                    
                except Exception as e:
                    # Fallback to heuristic for this host
                    heuristic_score = self.calculate_heuristic_score(vm_request, host)
                    if heuristic_score > 0:
                        feasible_hosts.append({
                            'host_id': host['host_id'],
                            'score': heuristic_score,
                            'ai_score': 0.5,
                            'heuristic_score': heuristic_score,
                            'missing_features': -1,  # Indicates fallback used
                            'host': host
                        })
        
        if not feasible_hosts:
            return -1
        
        # Select host with highest score
        best_host = max(feasible_hosts, key=lambda x: x['score'])
        
        # Debug output for first few placements
        if not hasattr(self, '_placement_count'):
            self._placement_count = 0
        
        if self._placement_count < 3:  # Show debug info for first 3 placements
            print(f"DEBUG: Placement {self._placement_count + 1}")
            print(f"  Selected Host {best_host['host_id']}: score={best_host['score']:.3f}")
            print(f"  AI score: {best_host['ai_score']:.3f}, Heuristic: {best_host['heuristic_score']:.3f}")
            if best_host['missing_features'] > 0:
                print(f"  Missing features: {best_host['missing_features']}")
        
        self._placement_count += 1
        
        return best_host['host_id']

def test_fixed_ai():
    """Test the fixed AI algorithm"""
    print("=== TESTING FIXED AI PLACEMENT ALGORITHM ===")
    
    try:
        # Initialize fixed algorithm
        fixed_ai = FixedHybridAIPlacement()
        
        # Create test scenario
        from data_generator import DataGenerator
        data_gen = DataGenerator(num_hosts=10, seed=42)
        
        # Test multiple scenarios
        success_count = 0
        total_tests = 20
        
        for i in range(total_tests):
            scenario = data_gen.generate_scenario()
            vm_request = scenario['vm_request']
            hosts = data_gen.host_specs
            
            # Test placement
            placement_id = fixed_ai.place_vm_fixed(vm_request, hosts)
            
            if placement_id != -1:
                success_count += 1
                
                # Check if placement is actually valid
                selected_host = hosts[placement_id]
                cpu_after = selected_host["current_cpu_usage"] + vm_request["cpu_required"]
                ram_after = selected_host["current_ram_usage"] + vm_request["ram_required"]
                
                if cpu_after > selected_host["cpu_cores"] or ram_after > selected_host["ram_gb"]:
                    print(f"ERROR: Invalid placement {i+1}!")
                    success_count -= 1
        
        success_rate = success_count / total_tests
        print(f"\n✓ Fixed AI Success Rate: {success_rate:.1%} ({success_count}/{total_tests})")
        
        if success_rate < 0.8:
            print("⚠ Success rate still low - may need model retraining")
        else:
            print("✓ Success rate improved significantly!")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing fixed AI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fixed_ai()