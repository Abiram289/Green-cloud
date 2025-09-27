"""
VM Placement Simulator and Evaluation System

This module provides a comprehensive simulation environment for testing
VM placement algorithms and comparing their performance across multiple metrics.
"""

import numpy as np
import pandas as pd
import json
import random
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from placement_algorithms import (
    get_all_algorithms, PlacementMetricsCalculator, 
    AIPredictorPlacement, BestFitPlacement, FirstFitPlacement,
    WorstFitPlacement, RandomPlacement, RoundRobinPlacement
)

class VMPlacementSimulator:
    """VM Placement Simulation Environment"""
    
    def __init__(self, host_specs_path: str = "data/host_specifications.json"):
        """
        Initialize the simulator
        
        Args:
            host_specs_path: Path to host specifications JSON file
        """
        self.load_host_specifications(host_specs_path)
        self.algorithms = {}
        self.results = {}
        
    def load_host_specifications(self, host_specs_path: str):
        """Load host specifications from JSON file"""
        with open(host_specs_path, 'r') as f:
            self.initial_host_specs = json.load(f)
        print(f"Loaded {len(self.initial_host_specs)} host specifications")
    
    def reset_host_states(self):
        """Reset all hosts to initial state"""
        self.hosts = []
        for spec in self.initial_host_specs:
            host = spec.copy()
            # Reset to low initial utilization
            host["current_cpu_usage"] = np.random.uniform(0, host["cpu_cores"] * 0.2)
            host["current_ram_usage"] = np.random.uniform(0, host["ram_gb"] * 0.2)
            self.hosts.append(host)
    
    def generate_vm_requests(self, num_requests: int = 500) -> List[Dict]:
        """Generate a batch of VM requests for simulation"""
        vm_types = [
            {"cpu": 1, "ram": 2, "type": "micro", "sla_requirement": 0.99, "weight": 0.4},
            {"cpu": 2, "ram": 4, "type": "small", "sla_requirement": 0.995, "weight": 0.3},
            {"cpu": 4, "ram": 8, "type": "medium", "sla_requirement": 0.99, "weight": 0.2},
            {"cpu": 8, "ram": 16, "type": "large", "sla_requirement": 0.999, "weight": 0.08},
            {"cpu": 16, "ram": 32, "type": "xlarge", "sla_requirement": 0.9995, "weight": 0.02},
        ]
        
        # Create weighted selection
        weights = [vt["weight"] for vt in vm_types]
        
        requests = []
        for i in range(num_requests):
            vm_type = random.choices(vm_types, weights=weights)[0]
            
            # Add some variation
            cpu_variation = 0.8 + np.random.random() * 0.4
            ram_variation = 0.8 + np.random.random() * 0.4
            
            request = {
                "vm_id": f"sim_vm_{i}",
                "cpu_required": max(1, int(vm_type["cpu"] * cpu_variation)),
                "ram_required": max(1, int(vm_type["ram"] * ram_variation)),
                "vm_type": vm_type["type"],
                "sla_requirement": vm_type["sla_requirement"],
                "expected_runtime_hours": np.random.exponential(24),
                "priority": np.random.choice(["low", "medium", "high"], p=[0.5, 0.3, 0.2])
            }
            requests.append(request)
        
        return requests
    
    def run_algorithm_simulation(self, algorithm, vm_requests: List[Dict]) -> Tuple[List[int], Dict]:
        """Run simulation for a single algorithm"""
        self.reset_host_states()
        placements = []
        
        print(f"Running simulation for {algorithm.name}...")
        
        for i, vm_request in enumerate(vm_requests):
            if i % 100 == 0 and i > 0:
                print(f"  Progress: {i}/{len(vm_requests)}")
            
            # Get placement decision from algorithm
            host_id = algorithm.place_vm(vm_request, self.hosts)
            placements.append(host_id)
            
            # Update host state if placement successful
            if host_id != -1:
                for host in self.hosts:
                    if host["host_id"] == host_id:
                        host["current_cpu_usage"] += vm_request["cpu_required"]
                        host["current_ram_usage"] += vm_request["ram_required"]
                        break
        
        # Calculate metrics
        metrics = PlacementMetricsCalculator.calculate_metrics(
            self.initial_host_specs, vm_requests, placements
        )
        
        return placements, metrics
    
    def run_comprehensive_evaluation(self, num_vm_requests: int = 500, num_runs: int = 3) -> Dict:
        """Run comprehensive evaluation comparing all algorithms"""
        print(f"Starting comprehensive evaluation with {num_vm_requests} VM requests over {num_runs} runs...")
        
        # Initialize results storage
        all_results = {}
        algorithms = get_all_algorithms()
        
        for run in range(num_runs):
            print(f"\\n{'='*50}")
            print(f"SIMULATION RUN {run + 1}/{num_runs}")
            print(f"{'='*50}")
            
            # Generate VM requests for this run
            vm_requests = self.generate_vm_requests(num_vm_requests)
            
            for algorithm in algorithms:
                try:
                    placements, metrics = self.run_algorithm_simulation(algorithm, vm_requests)
                    
                    if algorithm.name not in all_results:
                        all_results[algorithm.name] = {
                            'metrics_per_run': [],
                            'placements_per_run': []
                        }
                    
                    all_results[algorithm.name]['metrics_per_run'].append(metrics)
                    all_results[algorithm.name]['placements_per_run'].append(placements)
                    
                    print(f"  {algorithm.name}: {metrics['successful_placements']}/{len(vm_requests)} successful placements")
                
                except Exception as e:
                    print(f"  ERROR with {algorithm.name}: {str(e)}")
                    continue
        
        # Aggregate results across runs
        final_results = {}
        for algorithm_name, data in all_results.items():
            metrics_list = data['metrics_per_run']
            
            # Calculate mean and standard deviation for each metric
            aggregated_metrics = {}
            for metric_key in metrics_list[0].keys():
                values = [m[metric_key] for m in metrics_list]
                aggregated_metrics[f"{metric_key}_mean"] = np.mean(values)
                aggregated_metrics[f"{metric_key}_std"] = np.std(values)
                aggregated_metrics[f"{metric_key}_values"] = values
            
            final_results[algorithm_name] = aggregated_metrics
        
        self.results = final_results
        return final_results
    
    def create_comparison_summary(self) -> pd.DataFrame:
        """Create a summary DataFrame for easy comparison"""
        if not self.results:
            print("No results available. Run evaluation first.")
            return None
        
        summary_data = []
        key_metrics = [
            'total_energy_consumption', 'total_cost', 
            'average_cpu_utilization', 'average_ram_utilization', 
            'sla_violations', 'placement_success_rate'
        ]
        
        for algorithm_name, results in self.results.items():
            row = {'Algorithm': algorithm_name}
            for metric in key_metrics:
                row[f"{metric}_mean"] = results[f"{metric}_mean"]
                row[f"{metric}_std"] = results[f"{metric}_std"]
            summary_data.append(row)
        
        return pd.DataFrame(summary_data)
    
    def print_results_summary(self):
        """Print a formatted summary of results"""
        if not self.results:
            print("No results available. Run evaluation first.")
            return
        
        print("\\n" + "="*80)
        print("VM PLACEMENT ALGORITHM COMPARISON RESULTS")
        print("="*80)
        
        # Create summary table
        summary = self.create_comparison_summary()
        
        print("\\n1. ENERGY CONSUMPTION (Watts)")
        print("-" * 40)
        energy_sorted = summary.sort_values('total_energy_consumption_mean')
        for _, row in energy_sorted.iterrows():
            print(f"{row['Algorithm']:15}: {row['total_energy_consumption_mean']:8.1f} ± {row['total_energy_consumption_std']:6.1f}")
        
        print("\\n2. TOTAL COST ($)")
        print("-" * 40)
        cost_sorted = summary.sort_values('total_cost_mean')
        for _, row in cost_sorted.iterrows():
            print(f"{row['Algorithm']:15}: {row['total_cost_mean']:8.1f} ± {row['total_cost_std']:6.1f}")
        
        print("\\n3. AVERAGE CPU UTILIZATION (%)")
        print("-" * 40)
        cpu_sorted = summary.sort_values('average_cpu_utilization_mean', ascending=False)
        for _, row in cpu_sorted.iterrows():
            print(f"{row['Algorithm']:15}: {row['average_cpu_utilization_mean']*100:8.1f}% ± {row['average_cpu_utilization_std']*100:6.1f}%")
        
        print("\\n4. AVERAGE RAM UTILIZATION (%)")
        print("-" * 40)
        ram_sorted = summary.sort_values('average_ram_utilization_mean', ascending=False)
        for _, row in ram_sorted.iterrows():
            print(f"{row['Algorithm']:15}: {row['average_ram_utilization_mean']*100:8.1f}% ± {row['average_ram_utilization_std']*100:6.1f}%")
        
        print("\\n5. SLA VIOLATIONS (Count)")
        print("-" * 40)
        sla_sorted = summary.sort_values('sla_violations_mean')
        for _, row in sla_sorted.iterrows():
            print(f"{row['Algorithm']:15}: {row['sla_violations_mean']:8.1f} ± {row['sla_violations_std']:6.1f}")
        
        print("\\n6. PLACEMENT SUCCESS RATE (%)")
        print("-" * 40)
        success_sorted = summary.sort_values('placement_success_rate_mean', ascending=False)
        for _, row in success_sorted.iterrows():
            print(f"{row['Algorithm']:15}: {row['placement_success_rate_mean']*100:8.1f}% ± {row['placement_success_rate_std']*100:6.1f}%")
        
        # Calculate improvement over baselines
        print("\\n" + "="*80)
        print("AI-PREDICTOR IMPROVEMENTS OVER BASELINES")
        print("="*80)
        
        if 'AI-Predictor' in self.results:
            ai_results = self.results['AI-Predictor']
            baselines = ['Best-Fit', 'First-Fit', 'Random', 'Worst-Fit', 'Round-Robin']
            
            improvements = {}
            for baseline in baselines:
                if baseline in self.results:
                    baseline_results = self.results[baseline]
                    improvements[baseline] = {}
                    
                    # Energy improvement (lower is better)
                    energy_improvement = (baseline_results['total_energy_consumption_mean'] - 
                                        ai_results['total_energy_consumption_mean']) / baseline_results['total_energy_consumption_mean'] * 100
                    improvements[baseline]['energy'] = energy_improvement
                    
                    # Cost improvement (lower is better)
                    cost_improvement = (baseline_results['total_cost_mean'] - 
                                      ai_results['total_cost_mean']) / baseline_results['total_cost_mean'] * 100
                    improvements[baseline]['cost'] = cost_improvement
                    
                    # SLA improvement (lower violations is better)
                    if baseline_results['sla_violations_mean'] > 0:
                        sla_improvement = (baseline_results['sla_violations_mean'] - 
                                         ai_results['sla_violations_mean']) / baseline_results['sla_violations_mean'] * 100
                    else:
                        sla_improvement = 0
                    improvements[baseline]['sla'] = sla_improvement
            
            # Print improvements
            for baseline, impr in improvements.items():
                print(f"\\nVs {baseline}:")
                print(f"  Energy Reduction: {impr['energy']:6.1f}%")
                print(f"  Cost Reduction:   {impr['cost']:6.1f}%")
                print(f"  SLA Improvement:  {impr['sla']:6.1f}%")
    
    def plot_comparison_charts(self):
        """Create comprehensive comparison charts"""
        if not self.results:
            print("No results available. Run evaluation first.")
            return
        
        summary = self.create_comparison_summary()
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('VM Placement Algorithm Performance Comparison', fontsize=16, fontweight='bold')
        
        # 1. Energy Consumption
        ax1 = axes[0, 0]
        algorithms = summary['Algorithm']
        energy_means = summary['total_energy_consumption_mean']
        energy_stds = summary['total_energy_consumption_std']
        
        bars1 = ax1.bar(algorithms, energy_means, yerr=energy_stds, capsize=5)
        ax1.set_title('Energy Consumption (Watts)', fontweight='bold')
        ax1.set_ylabel('Watts')
        ax1.tick_params(axis='x', rotation=45)
        
        # Color AI-Predictor differently
        for i, bar in enumerate(bars1):
            if algorithms.iloc[i] == 'AI-Predictor':
                bar.set_color('red')
                bar.set_alpha(0.8)
        
        # 2. Cost
        ax2 = axes[0, 1]
        cost_means = summary['total_cost_mean']
        cost_stds = summary['total_cost_std']
        
        bars2 = ax2.bar(algorithms, cost_means, yerr=cost_stds, capsize=5)
        ax2.set_title('Total Cost ($)', fontweight='bold')
        ax2.set_ylabel('Dollars')
        ax2.tick_params(axis='x', rotation=45)
        
        for i, bar in enumerate(bars2):
            if algorithms.iloc[i] == 'AI-Predictor':
                bar.set_color('red')
                bar.set_alpha(0.8)
        
        # 3. CPU Utilization
        ax3 = axes[0, 2]
        cpu_means = summary['average_cpu_utilization_mean'] * 100
        cpu_stds = summary['average_cpu_utilization_std'] * 100
        
        bars3 = ax3.bar(algorithms, cpu_means, yerr=cpu_stds, capsize=5)
        ax3.set_title('Average CPU Utilization (%)', fontweight='bold')
        ax3.set_ylabel('Percentage')
        ax3.tick_params(axis='x', rotation=45)
        
        for i, bar in enumerate(bars3):
            if algorithms.iloc[i] == 'AI-Predictor':
                bar.set_color('red')
                bar.set_alpha(0.8)
        
        # 4. RAM Utilization
        ax4 = axes[1, 0]
        ram_means = summary['average_ram_utilization_mean'] * 100
        ram_stds = summary['average_ram_utilization_std'] * 100
        
        bars4 = ax4.bar(algorithms, ram_means, yerr=ram_stds, capsize=5)
        ax4.set_title('Average RAM Utilization (%)', fontweight='bold')
        ax4.set_ylabel('Percentage')
        ax4.tick_params(axis='x', rotation=45)
        
        for i, bar in enumerate(bars4):
            if algorithms.iloc[i] == 'AI-Predictor':
                bar.set_color('red')
                bar.set_alpha(0.8)
        
        # 5. SLA Violations
        ax5 = axes[1, 1]
        sla_means = summary['sla_violations_mean']
        sla_stds = summary['sla_violations_std']
        
        bars5 = ax5.bar(algorithms, sla_means, yerr=sla_stds, capsize=5)
        ax5.set_title('SLA Violations (Count)', fontweight='bold')
        ax5.set_ylabel('Count')
        ax5.tick_params(axis='x', rotation=45)
        
        for i, bar in enumerate(bars5):
            if algorithms.iloc[i] == 'AI-Predictor':
                bar.set_color('red')
                bar.set_alpha(0.8)
        
        # 6. Success Rate
        ax6 = axes[1, 2]
        success_means = summary['placement_success_rate_mean'] * 100
        success_stds = summary['placement_success_rate_std'] * 100
        
        bars6 = ax6.bar(algorithms, success_means, yerr=success_stds, capsize=5)
        ax6.set_title('Placement Success Rate (%)', fontweight='bold')
        ax6.set_ylabel('Percentage')
        ax6.tick_params(axis='x', rotation=45)
        
        for i, bar in enumerate(bars6):
            if algorithms.iloc[i] == 'AI-Predictor':
                bar.set_color('red')
                bar.set_alpha(0.8)
        
        plt.tight_layout()
        plt.savefig('results/algorithm_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_results(self, filename: str = "simulation_results.json"):
        """Save simulation results to file"""
        if not self.results:
            print("No results available to save.")
            return
        
        # Convert numpy types for JSON serialization
        json_results = {}
        for algorithm_name, data in self.results.items():
            json_results[algorithm_name] = {}
            for key, value in data.items():
                if isinstance(value, np.ndarray):
                    json_results[algorithm_name][key] = value.tolist()
                elif isinstance(value, list):
                    json_results[algorithm_name][key] = value
                else:
                    json_results[algorithm_name][key] = float(value)
        
        filepath = f"results/{filename}"
        with open(filepath, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"Results saved to {filepath}")
        
        # Also save summary CSV
        summary = self.create_comparison_summary()
        summary.to_csv("results/algorithm_comparison_summary.csv", index=False)
        print("Summary saved to results/algorithm_comparison_summary.csv")

def main():
    """Main simulation function"""
    print("VM Placement Algorithm Evaluation System")
    print("="*50)
    
    # Initialize simulator
    simulator = VMPlacementSimulator()
    
    # Run comprehensive evaluation
    results = simulator.run_comprehensive_evaluation(num_vm_requests=1000, num_runs=5)
    
    # Print results
    simulator.print_results_summary()
    
    # Create visualizations
    simulator.plot_comparison_charts()
    
    # Save results
    simulator.save_results()
    
    return simulator

if __name__ == "__main__":
    main()