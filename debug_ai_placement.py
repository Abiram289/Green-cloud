#!/usr/bin/env python3
"""
Debug AI Placement Algorithm
Test AI performance directly and identify issues
"""

import sys
import os
sys.path.append('src')

import numpy as np
import pandas as pd
import joblib
from enhanced_algorithms import HybridAIPredictorPlacement
from data_generator import DataGenerator
import json

def debug_ai_placement():
    print("=== AI PLACEMENT DEBUG ANALYSIS ===")
    
    # 1. Check model files
    print("\n1. Checking model files...")
    try:
        hybrid_predictor = joblib.load("models/hybrid_ai_predictor.pkl")
        print(f"✓ Hybrid AI predictor loaded: {type(hybrid_predictor)}")
        print(f"  Keys: {list(hybrid_predictor.keys())}")
        
        scaler = joblib.load('models/scaler_standard.pkl')
        print(f"✓ Scaler loaded: {type(scaler)}")
        
        with open('models/advanced_models_metadata.json', 'r') as f:
            metadata = json.load(f)
        print(f"✓ Metadata loaded: {len(metadata['feature_columns'])} features")
        
    except Exception as e:
        print(f"✗ Error loading models: {e}")
        return False
    
    # 2. Test feature preparation
    print("\n2. Testing feature preparation...")
    try:
        ai_algo = HybridAIPredictorPlacement()
        
        # Create test data
        data_gen = DataGenerator(num_hosts=5, num_scenarios=1, seed=42)
        scenario = data_gen.generate_scenario()
        
        vm_request = scenario['vm_request']
        hosts = data_gen.host_specs
        
        print(f"✓ AI algorithm initialized")
        print(f"  VM request: CPU={vm_request['cpu_required']}, RAM={vm_request['ram_required']}")
        print(f"  Number of hosts: {len(hosts)}")
        
        # Test feature preparation for first host
        test_host = hosts[0]
        features = ai_algo.prepare_features(vm_request, test_host)
        print(f"✓ Features prepared: shape {features.shape}")
        
        # Check if all required features are present
        missing_features = []
        for col in ai_algo.feature_columns:
            if col not in [f"feature_{i}" for i in range(features.shape[1])]:
                missing_features.append(col)
        
        if missing_features:
            print(f"⚠ Missing features: {len(missing_features)} features not properly mapped")
        
    except Exception as e:
        print(f"✗ Error in feature preparation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Test placement decision
    print("\n3. Testing placement decision...")
    try:
        placement_id = ai_algo.place_vm(vm_request, hosts)
        print(f"✓ Placement decision: Host {placement_id}")
        
        if placement_id == -1:
            print("⚠ AI algorithm returned -1 (no placement found)")
        else:
            selected_host = hosts[placement_id]
            cpu_util_after = (selected_host["current_cpu_usage"] + vm_request["cpu_required"]) / selected_host["cpu_cores"]
            ram_util_after = (selected_host["current_ram_usage"] + vm_request["ram_required"]) / selected_host["ram_gb"]
            print(f"  Host specs: CPU={selected_host['cpu_cores']}, RAM={selected_host['ram_gb']}GB")
            print(f"  Utilization after: CPU={cpu_util_after:.2%}, RAM={ram_util_after:.2%}")
            
    except Exception as e:
        print(f"✗ Error in placement decision: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. Compare with traditional algorithms
    print("\n4. Comparing with traditional algorithms...")
    try:
        from enhanced_algorithms import LoadBalancingBestFit
        from placement_algorithms import BestFitAlgorithm, WorstFitAlgorithm
        
        # Test traditional algorithms
        best_fit = BestFitAlgorithm()
        worst_fit = WorstFitAlgorithm()
        lb_best_fit = LoadBalancingBestFit()
        
        bf_placement = best_fit.place_vm(vm_request, hosts)
        wf_placement = worst_fit.place_vm(vm_request, hosts)
        lbbf_placement = lb_best_fit.place_vm(vm_request, hosts)
        
        print(f"  AI Placement: Host {placement_id}")
        print(f"  Best-Fit: Host {bf_placement}")
        print(f"  Worst-Fit: Host {wf_placement}")
        print(f"  LB-Best-Fit: Host {lbbf_placement}")
        
        # Check if they're all different
        if placement_id == bf_placement == wf_placement:
            print("⚠ All algorithms chose the same host - may indicate limited choice or identical logic")
        
    except Exception as e:
        print(f"✗ Error comparing algorithms: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Analyze model prediction scores
    print("\n5. Analyzing model prediction scores...")
    try:
        feasible_hosts = []
        for i, host in enumerate(hosts):
            if ai_algo.can_place_vm(vm_request, host):
                features = ai_algo.prepare_features(vm_request, host)
                features_scaled = ai_algo.scaler.transform(features)
                
                # Get main model prediction
                main_prob = ai_algo.main_model.predict_proba(features_scaled)[0][1]
                
                # Get specialized scores if available
                specialized_scores = ai_algo.get_multi_objective_scores(vm_request, host)
                
                feasible_hosts.append({
                    'host_id': i,
                    'main_prob': main_prob,
                    'specialized_scores': specialized_scores,
                    'cpu_util_after': (host["current_cpu_usage"] + vm_request["cpu_required"]) / host["cpu_cores"],
                    'ram_util_after': (host["current_ram_usage"] + vm_request["ram_required"]) / host["ram_gb"]
                })
        
        print(f"  Feasible hosts: {len(feasible_hosts)}")
        for host_info in feasible_hosts:
            print(f"    Host {host_info['host_id']}: main_prob={host_info['main_prob']:.3f}, "
                  f"CPU={host_info['cpu_util_after']:.2%}, RAM={host_info['ram_util_after']:.2%}")
        
        # Check if AI is making reasonable predictions
        if feasible_hosts:
            probs = [h['main_prob'] for h in feasible_hosts]
            if max(probs) - min(probs) < 0.1:
                print("⚠ AI predictions are too similar - model may not be discriminative enough")
            if all(p < 0.6 for p in probs):
                print("⚠ All AI predictions are low confidence - model may be poorly trained")
                
    except Exception as e:
        print(f"✗ Error analyzing predictions: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n=== DEBUG ANALYSIS COMPLETE ===")
    return True

if __name__ == "__main__":
    debug_ai_placement()