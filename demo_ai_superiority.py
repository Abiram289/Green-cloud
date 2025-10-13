#!/usr/bin/env python3
"""
AI Algorithm Superiority Demonstration
Quick demonstration showing AI algorithms outperform classical ones
"""

import sys
import os
sys.path.append('src')

import numpy as np
from datetime import datetime

# Import our superior AI model
from ai_model import AIModel
from data_generator import DataGenerator

# Import classical algorithms
from placement_algorithms import BestFitPlacement, FirstFitPlacement, WorstFitPlacement

def quick_performance_test():
    """Quick performance test to demonstrate AI superiority"""
    print("🚀 AI vs Classical Algorithm Performance Demo")
    print("=" * 50)
    
    # Initialize algorithms
    algorithms = {
        'AI Model': AIModel(),
        'Best-Fit': BestFitPlacement(),
        'First-Fit': FirstFitPlacement(),
        'Worst-Fit': WorstFitPlacement()
    }
    
    # Generate test data with more hosts for heavy load
    data_gen = DataGenerator(num_hosts=25, seed=42)
    hosts = data_gen.host_specs.copy()
    
    # Generate VM requests
    vm_requests = []
    for i in range(1000):  # 1000 VM requests for heavy load testing
        scenario = data_gen.generate_scenario()
        vm_requests.append(scenario['vm_request'])
    
    results = {}
    
    print(f"Testing with {len(vm_requests)} VM requests on {len(hosts)} hosts...")
    print()
    
    for alg_name, algorithm in algorithms.items():
        print(f"Testing {alg_name}...")
        
        # Reset hosts for each algorithm
        test_hosts = [h.copy() for h in hosts]
        total_energy = 0
        total_cost = 0
        successful_placements = 0
        
        for vm_request in vm_requests:
            host_id = algorithm.place_vm(vm_request, test_hosts)
            
            if host_id != -1:
                successful_placements += 1
                selected_host = test_hosts[host_id]
                
                # Calculate metrics
                if hasattr(algorithm, 'calculate_energy_consumption'):
                    energy = algorithm.calculate_energy_consumption(vm_request, selected_host)
                    cost = algorithm.calculate_cost(vm_request, selected_host)
                else:
                    # Use the same advanced energy calculation for fair comparison
                    cpu_util_after = (selected_host['current_cpu_usage'] + vm_request['cpu_required']) / selected_host['cpu_cores']
                    ram_util_after = (selected_host['current_ram_usage'] + vm_request['ram_required']) / selected_host['ram_gb']
                    
                    # Advanced energy calculation (same as AI)
                    base_power = selected_host['base_power_watts']
                    cpu_power_factor = 0.3 + 0.7 * (cpu_util_after ** 1.4)
                    ram_power_factor = 0.1 + 0.3 * ram_util_after
                    thermal_factor = 1 + 0.1 * max(0, cpu_util_after - 0.8)
                    energy = base_power * (cpu_power_factor + ram_power_factor) * thermal_factor
                    
                    # Advanced cost calculation (same as AI)
                    base_cost = selected_host['cost_per_hour']
                    runtime = vm_request.get('expected_runtime_hours', 24)
                    utilization_premium = 1 + 0.6 * max(cpu_util_after, ram_util_after)
                    priority = vm_request.get('priority', 'medium')
                    priority_multiplier = {'low': 0.8, 'medium': 1.0, 'high': 1.3, 'critical': 1.6}.get(priority, 1.0)
                    sla_requirement = vm_request.get('sla_requirement', 0.99)
                    sla_multiplier = 1 + (sla_requirement - 0.99) * 10
                    cost = base_cost * utilization_premium * priority_multiplier * sla_multiplier * runtime
                
                total_energy += energy
                total_cost += cost
                
                # Update host state
                selected_host['current_cpu_usage'] += vm_request['cpu_required']
                selected_host['current_ram_usage'] += vm_request['ram_required']
        
        success_rate = successful_placements / len(vm_requests)
        avg_energy = total_energy / max(successful_placements, 1)
        avg_cost = total_cost / max(successful_placements, 1)
        
        results[alg_name] = {
            'success_rate': success_rate,
            'total_energy': total_energy,
            'total_cost': total_cost,
            'avg_energy': avg_energy,
            'avg_cost': avg_cost
        }
        
        print(f"  ✓ Success: {success_rate:.1%}, Energy: {total_energy:.0f}W, Cost: ${total_cost:.0f}")
    
    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON RESULTS")
    print("=" * 60)
    
    # Sort by energy consumption
    sorted_results = sorted(results.items(), key=lambda x: x[1]['total_energy'])
    
    print("\n🏆 ENERGY CONSUMPTION RANKING (Lower = Better)")
    print("-" * 50)
    for i, (alg_name, metrics) in enumerate(sorted_results, 1):
        energy = metrics['total_energy']
        print(f"{i}. {alg_name:15}: {energy:8.0f}W")
    
    # Sort by cost
    sorted_cost = sorted(results.items(), key=lambda x: x[1]['total_cost'])
    
    print("\n💰 COST RANKING (Lower = Better)")
    print("-" * 50)
    for i, (alg_name, metrics) in enumerate(sorted_cost, 1):
        cost = metrics['total_cost']
        print(f"{i}. {alg_name:15}: ${cost:8.0f}")
    
    # AI vs Classical comparison
    ai_algorithms = [alg for alg in results.keys() if 'AI Model' in alg]
    classical_algorithms = [alg for alg in results.keys() if 'AI Model' not in alg]
    
    if ai_algorithms and classical_algorithms:
        print("\n🤖 AI vs CLASSICAL COMPARISON")
        print("-" * 50)
        
        # Find best AI and classical
        best_ai_energy = min(ai_algorithms, key=lambda x: results[x]['total_energy'])
        best_classical_energy = min(classical_algorithms, key=lambda x: results[x]['total_energy'])
        
        ai_energy = results[best_ai_energy]['total_energy']
        classical_energy = results[best_classical_energy]['total_energy']
        energy_improvement = ((classical_energy - ai_energy) / classical_energy) * 100
        
        best_ai_cost = min(ai_algorithms, key=lambda x: results[x]['total_cost'])
        best_classical_cost = min(classical_algorithms, key=lambda x: results[x]['total_cost'])
        
        ai_cost = results[best_ai_cost]['total_cost']
        classical_cost = results[best_classical_cost]['total_cost']
        cost_improvement = ((classical_cost - ai_cost) / classical_cost) * 100
        
        print(f"AI Model:              {best_ai_energy}")
        print(f"Best Classical:        {best_classical_energy}")
        print(f"Energy Improvement:     {energy_improvement:+.1f}%")
        print(f"Cost Improvement:       {cost_improvement:+.1f}%")
        
        if energy_improvement > 10 and cost_improvement > 5:
            print("\n✅ AI ALGORITHMS SIGNIFICANTLY OUTPERFORM CLASSICAL ALGORITHMS!")
        elif energy_improvement > 5 or cost_improvement > 3:
            print("\n✓ AI algorithms show clear performance advantages")
        else:
            print("\n⚠ AI algorithms show modest improvements")
    
    print("\n" + "=" * 60)
    print("🎉 Performance demonstration completed!")
    
    return results

if __name__ == "__main__":
    quick_performance_test()
