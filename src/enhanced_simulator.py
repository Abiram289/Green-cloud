"""
Enhanced VM Placement Simulator with Load Balancing and Advanced AI

This module provides an enhanced simulation environment with:
1. Load balancing metrics and analysis
2. Advanced AI algorithms
3. Comprehensive performance evaluation
4. Statistical analysis and visualization integration
"""

import numpy as np
import pandas as pd
import json
import random
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
try:
    import seaborn as sns
except ImportError:
    sns = None  # Seaborn is optional
try:
    from enhanced_algorithms import (
        get_enhanced_algorithms, EnhancedMetricsCalculator,
        HybridAIPredictorPlacement, LoadBalancingFirstFit, LoadBalancingBestFit,
        AdaptiveLoadBalancing
    )
except ImportError:
    # Fallback if enhanced_algorithms not available
    from placement_algorithms import get_all_algorithms
    print("Enhanced algorithms not available, using basic algorithms")
    
    def get_enhanced_algorithms():
        return get_all_algorithms()
    
    class EnhancedMetricsCalculator:
        @staticmethod
        def calculate_comprehensive_metrics(hosts, requests, placements, algorithm_name):
            from placement_algorithms import PlacementMetricsCalculator
            return PlacementMetricsCalculator.calculate_metrics(hosts, requests, placements)

class EnhancedVMPlacementSimulator:
    """Enhanced VM Placement Simulation Environment"""
    
    def __init__(self, host_specs_path: str = "data/host_specifications.json"):
        """
        Initialize the enhanced simulator
        
        Args:
            host_specs_path: Path to host specifications JSON file
        """
        self.load_host_specifications(host_specs_path)
        self.algorithms = {}
        self.results = {}
        self.enhanced_metrics = True
        
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
            # Reset to low initial utilization with some variation
            host["current_cpu_usage"] = np.random.uniform(0, host["cpu_cores"] * 0.15)
            host["current_ram_usage"] = np.random.uniform(0, host["ram_gb"] * 0.15)
            self.hosts.append(host)
    
    def generate_enhanced_vm_requests(self, num_requests: int = 1000) -> List[Dict]:
        """Generate enhanced VM requests with more realistic patterns"""
        vm_types = [
            {"cpu": 1, "ram": 2, "type": "micro", "sla_requirement": 0.99, "weight": 0.35},
            {"cpu": 2, "ram": 4, "type": "small", "sla_requirement": 0.995, "weight": 0.25},
            {"cpu": 4, "ram": 8, "type": "medium", "sla_requirement": 0.99, "weight": 0.25},
            {"cpu": 8, "ram": 16, "type": "large", "sla_requirement": 0.999, "weight": 0.10},
            {"cpu": 16, "ram": 32, "type": "xlarge", "sla_requirement": 0.9995, "weight": 0.05},
        ]
        
        # Create weighted selection
        weights = [vt["weight"] for vt in vm_types]
        
        requests = []
        for i in range(num_requests):
            vm_type = random.choices(vm_types, weights=weights)[0]
            
            # Add realistic variation
            cpu_variation = 0.7 + np.random.random() * 0.6  # ±30% variation
            ram_variation = 0.7 + np.random.random() * 0.6
            
            # Runtime follows more realistic distribution
            runtime_type = np.random.choice(['short', 'medium', 'long'], p=[0.4, 0.4, 0.2])
            if runtime_type == 'short':
                runtime = np.random.exponential(4)  # Average 4 hours
            elif runtime_type == 'medium':
                runtime = np.random.exponential(24)  # Average 24 hours  
            else:
                runtime = np.random.exponential(168)  # Average 1 week
            
            request = {
                "vm_id": f"enhanced_vm_{i}",
                "cpu_required": max(1, int(vm_type["cpu"] * cpu_variation)),
                "ram_required": max(1, int(vm_type["ram"] * ram_variation)),
                "vm_type": vm_type["type"],
                "sla_requirement": vm_type["sla_requirement"],
                "expected_runtime_hours": max(1, runtime),
                "priority": np.random.choice(["low", "medium", "high"], p=[0.4, 0.4, 0.2])
            }
            requests.append(request)
        
        return requests
    
    def run_enhanced_algorithm_simulation(self, algorithm, vm_requests: List[Dict]) -> Tuple[List[int], Dict]:
        """Run enhanced simulation for a single algorithm"""
        self.reset_host_states()
        placements = []
        
        print(f"Running enhanced simulation for {algorithm.name}...")
        
        # Track additional metrics
        placement_times = []
        load_balance_evolution = []
        
        for i, vm_request in enumerate(vm_requests):
            if i % 100 == 0 and i > 0:
                print(f"  Progress: {i}/{len(vm_requests)}")
            
            # Record load balance before placement
            if hasattr(algorithm, 'calculate_load_balancing_score'):
                lb_before = algorithm.calculate_load_balancing_score(self.hosts)
                load_balance_evolution.append(lb_before)
            
            # Time the placement decision
            import time
            start_time = time.time()
            host_id = algorithm.place_vm(vm_request, self.hosts)
            placement_time = time.time() - start_time
            placement_times.append(placement_time)
            
            placements.append(host_id)
            
            # Update host state if placement successful
            if host_id != -1:
                for host in self.hosts:
                    if host["host_id"] == host_id:
                        host["current_cpu_usage"] += vm_request["cpu_required"]
                        host["current_ram_usage"] += vm_request["ram_required"]
                        break
        
        # Calculate enhanced metrics
        try:
            if self.enhanced_metrics:
                metrics = EnhancedMetricsCalculator.calculate_comprehensive_metrics(
                    self.initial_host_specs, vm_requests, placements, algorithm.name
                )
            else:
                # Fallback to basic metrics
                from placement_algorithms import PlacementMetricsCalculator
                metrics = PlacementMetricsCalculator.calculate_metrics(
                    self.initial_host_specs, vm_requests, placements
                )
        except Exception as e:
            # Double fallback to basic metrics
            from placement_algorithms import PlacementMetricsCalculator
            metrics = PlacementMetricsCalculator.calculate_metrics(
                self.initial_host_specs, vm_requests, placements
            )
        
        # Add timing and load balance metrics
        metrics.update({
            'average_placement_time': np.mean(placement_times),
            'total_placement_time': sum(placement_times),
            'placement_time_std': np.std(placement_times),
            'load_balance_evolution': load_balance_evolution[-10:] if load_balance_evolution else []  # Last 10 for storage
        })
        
        return placements, metrics
    
    def run_comprehensive_enhanced_evaluation(self, num_vm_requests: int = 1000, num_runs: int = 3) -> Dict:
        """Run comprehensive enhanced evaluation"""
        print(f"Starting comprehensive enhanced evaluation with {num_vm_requests} VM requests over {num_runs} runs...")
        
        # Initialize results storage
        all_results = {}
        
        # Get enhanced algorithms (includes traditional ones for comparison)
        try:
            algorithms = get_enhanced_algorithms()
        except Exception as e:
            print(f"Error loading enhanced algorithms: {e}")
            print("Falling back to basic algorithms...")
            from placement_algorithms import (
                BestFitPlacement, FirstFitPlacement, WorstFitPlacement,
                RandomPlacement, RoundRobinPlacement
            )
            # Use basic algorithms only (exclude AI-based ones)
            algorithms = [
                BestFitPlacement(),
                FirstFitPlacement(), 
                WorstFitPlacement(),
                RandomPlacement(),
                RoundRobinPlacement()
            ]
            self.enhanced_metrics = False
        
        for run in range(num_runs):
            print(f"\n{'='*60}")
            print(f"ENHANCED SIMULATION RUN {run + 1}/{num_runs}")
            print(f"{'='*60}")
            
            # Generate enhanced VM requests for this run
            vm_requests = self.generate_enhanced_vm_requests(num_vm_requests)
            
            for algorithm in algorithms:
                try:
                    placements, metrics = self.run_enhanced_algorithm_simulation(algorithm, vm_requests)
                    
                    if algorithm.name not in all_results:
                        all_results[algorithm.name] = {
                            'metrics_per_run': [],
                            'placements_per_run': []
                        }
                    
                    all_results[algorithm.name]['metrics_per_run'].append(metrics)
                    all_results[algorithm.name]['placements_per_run'].append(placements)
                    
                    # Print key metrics
                    success_rate = metrics['successful_placements'] / len(vm_requests)
                    energy = metrics.get('total_energy_consumption', 0)
                    cost = metrics.get('total_cost', 0)
                    
                    print(f"  {algorithm.name:20}: Success: {success_rate:.3f}, Energy: {energy:6.0f}W, Cost: ${cost:6.0f}")
                    
                    # Print enhanced metrics if available
                    if 'cpu_load_balancing_index' in metrics:
                        lb_index = metrics['cpu_load_balancing_index']
                        fairness = metrics.get('overall_fairness', 0)
                        print(f"    {'':22}LB Index: {lb_index:.3f}, Fairness: {fairness:.3f}")
                
                except Exception as e:
                    print(f"  ERROR with {algorithm.name}: {str(e)}")
                    continue
        
        # Aggregate results across runs
        final_results = {}
        for algorithm_name, data in all_results.items():
            metrics_list = data['metrics_per_run']
            
            # Calculate mean and standard deviation for each metric
            aggregated_metrics = {}
            if metrics_list:
                for metric_key in metrics_list[0].keys():
                    if metric_key in ['load_balance_evolution']:  # Skip complex objects
                        continue
                    
                    values = []
                    for m in metrics_list:
                        val = m.get(metric_key, 0)
                        if isinstance(val, (int, float)) and not np.isnan(val) and not np.isinf(val):
                            values.append(val)
                    
                    if values:
                        aggregated_metrics[f"{metric_key}_mean"] = np.mean(values)
                        aggregated_metrics[f"{metric_key}_std"] = np.std(values)
                        aggregated_metrics[f"{metric_key}_values"] = values
            
            final_results[algorithm_name] = aggregated_metrics
        
        self.results = final_results
        return final_results
    
    def create_enhanced_comparison_summary(self) -> pd.DataFrame:
        """Create enhanced summary DataFrame with load balancing metrics"""
        if not self.results:
            print("No results available. Run evaluation first.")
            return None
        
        summary_data = []
        
        # Define all metrics to include
        key_metrics = [
            'total_energy_consumption', 'total_cost', 
            'average_cpu_utilization', 'average_ram_utilization', 
            'sla_violations', 'placement_success_rate'
        ]
        
        # Add load balancing metrics if available
        enhanced_metrics = [
            'cpu_load_balancing_index', 'ram_load_balancing_index',
            'cpu_fairness_index', 'ram_fairness_index',
            'cpu_variance', 'ram_variance',
            'average_placement_time'
        ]
        
        for algorithm_name, results in self.results.items():
            row = {'Algorithm': algorithm_name}
            
            # Add standard metrics
            for metric in key_metrics:
                mean_key = f"{metric}_mean"
                std_key = f"{metric}_std"
                if mean_key in results:
                    row[mean_key] = results[mean_key]
                    row[std_key] = results.get(std_key, 0)
            
            # Add enhanced metrics if available
            for metric in enhanced_metrics:
                mean_key = f"{metric}_mean"
                std_key = f"{metric}_std"
                if mean_key in results:
                    row[mean_key] = results[mean_key]
                    row[std_key] = results.get(std_key, 0)
            
            summary_data.append(row)
        
        return pd.DataFrame(summary_data)
    
    def print_enhanced_results_summary(self):
        """Print enhanced formatted summary of results"""
        if not self.results:
            print("No results available. Run evaluation first.")
            return
        
        print("\n" + "="*100)
        print("ENHANCED VM PLACEMENT ALGORITHM COMPARISON RESULTS")
        print("="*100)
        
        # Create enhanced summary table
        summary = self.create_enhanced_comparison_summary()
        if summary is None:
            return
        
        # Standard performance metrics
        print("\n📊 PERFORMANCE METRICS")
        print("-" * 50)
        
        print("\n1. ENERGY CONSUMPTION (Watts)")
        print("-" * 40)
        if 'total_energy_consumption_mean' in summary.columns:
            energy_sorted = summary.sort_values('total_energy_consumption_mean')
            for _, row in energy_sorted.iterrows():
                energy_mean = row.get('total_energy_consumption_mean', 0)
                energy_std = row.get('total_energy_consumption_std', 0)
                print(f"{row['Algorithm']:20}: {energy_mean:8.1f} ± {energy_std:6.1f}")
        
        print("\n2. TOTAL COST ($)")
        print("-" * 40)
        if 'total_cost_mean' in summary.columns:
            cost_sorted = summary.sort_values('total_cost_mean')
            for _, row in cost_sorted.iterrows():
                cost_mean = row.get('total_cost_mean', 0)
                cost_std = row.get('total_cost_std', 0)
                print(f"{row['Algorithm']:20}: {cost_mean:8.1f} ± {cost_std:6.1f}")
        
        print("\n3. RESOURCE UTILIZATION (%)")
        print("-" * 40)
        if 'average_cpu_utilization_mean' in summary.columns:
            for _, row in summary.iterrows():
                cpu_mean = row.get('average_cpu_utilization_mean', 0) * 100
                cpu_std = row.get('average_cpu_utilization_std', 0) * 100
                ram_mean = row.get('average_ram_utilization_mean', 0) * 100
                ram_std = row.get('average_ram_utilization_std', 0) * 100
                print(f"{row['Algorithm']:20}: CPU {cpu_mean:5.1f}% ± {cpu_std:4.1f}%, RAM {ram_mean:5.1f}% ± {ram_std:4.1f}%")
        
        # Load balancing metrics
        if any('cpu_load_balancing_index_mean' in str(col) for col in summary.columns):
            print("\n⚖️  LOAD BALANCING METRICS")
            print("-" * 50)
            
            print("\n4. LOAD BALANCING INDEX (Lower = Better)")
            print("-" * 40)
            if 'cpu_load_balancing_index_mean' in summary.columns:
                lb_sorted = summary.sort_values('cpu_load_balancing_index_mean')
                for _, row in lb_sorted.iterrows():
                    cpu_lb = row.get('cpu_load_balancing_index_mean', 0)
                    ram_lb = row.get('ram_load_balancing_index_mean', 0)
                    combined_lb = (cpu_lb + ram_lb) / 2
                    print(f"{row['Algorithm']:20}: Combined {combined_lb:6.3f} (CPU: {cpu_lb:.3f}, RAM: {ram_lb:.3f})")
            
            print("\n5. FAIRNESS INDEX (Higher = Better)")
            print("-" * 40)
            if 'cpu_fairness_index_mean' in summary.columns:
                fairness_sorted = summary.sort_values('cpu_fairness_index_mean', ascending=False)
                for _, row in fairness_sorted.iterrows():
                    cpu_fair = row.get('cpu_fairness_index_mean', 0)
                    ram_fair = row.get('ram_fairness_index_mean', 0)
                    combined_fair = (cpu_fair + ram_fair) / 2
                    print(f"{row['Algorithm']:20}: Combined {combined_fair:6.3f} (CPU: {cpu_fair:.3f}, RAM: {ram_fair:.3f})")
        
        # Performance analysis
        print("\n🎯 PERFORMANCE ANALYSIS")
        print("-" * 50)
        
        if 'AI' in str(self.results.keys()) or 'Hybrid' in str(self.results.keys()):
            ai_algorithms = [alg for alg in self.results.keys() if 'AI' in alg or 'Hybrid' in alg]
            traditional_algorithms = [alg for alg in self.results.keys() if alg not in ai_algorithms]
            
            print(f"\n🤖 AI Algorithms: {', '.join(ai_algorithms)}")
            print(f"📊 Traditional: {', '.join(traditional_algorithms[:3])}{'...' if len(traditional_algorithms) > 3 else ''}")
            
            # Compare AI vs best traditional
            if ai_algorithms and traditional_algorithms:
                print("\n6. AI vs TRADITIONAL COMPARISON")
                print("-" * 40)
                
                # Find best AI and traditional algorithms by different metrics
                best_ai_energy = min(ai_algorithms, key=lambda x: self.results[x].get('total_energy_consumption_mean', float('inf')))
                best_trad_energy = min(traditional_algorithms, key=lambda x: self.results[x].get('total_energy_consumption_mean', float('inf')))
                
                ai_energy = self.results[best_ai_energy].get('total_energy_consumption_mean', 0)
                trad_energy = self.results[best_trad_energy].get('total_energy_consumption_mean', 0)
                
                if trad_energy > 0:
                    energy_improvement = (trad_energy - ai_energy) / trad_energy * 100
                    print(f"Best AI Energy ({best_ai_energy:10}): {energy_improvement:+6.1f}% vs {best_trad_energy}")
                
                # Cost comparison
                best_ai_cost = min(ai_algorithms, key=lambda x: self.results[x].get('total_cost_mean', float('inf')))
                best_trad_cost = min(traditional_algorithms, key=lambda x: self.results[x].get('total_cost_mean', float('inf')))
                
                ai_cost = self.results[best_ai_cost].get('total_cost_mean', 0)
                trad_cost = self.results[best_trad_cost].get('total_cost_mean', 0)
                
                if trad_cost > 0:
                    cost_improvement = (trad_cost - ai_cost) / trad_cost * 100
                    print(f"Best AI Cost   ({best_ai_cost:10}): {cost_improvement:+6.1f}% vs {best_trad_cost}")
        
        print("\n" + "="*100)
    
    def save_enhanced_results(self, filename: str = "enhanced_simulation_results.json"):
        """Save enhanced simulation results"""
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
                    # Handle nested lists/arrays
                    try:
                        json_results[algorithm_name][key] = [float(x) if isinstance(x, (int, float, np.number)) else x for x in value]
                    except:
                        json_results[algorithm_name][key] = str(value)  # Fallback to string
                elif isinstance(value, (int, float, np.number)):
                    json_results[algorithm_name][key] = float(value)
                else:
                    json_results[algorithm_name][key] = str(value)
        
        filepath = f"results/{filename}"
        with open(filepath, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"Enhanced results saved to {filepath}")
        
        # Save enhanced summary CSV
        summary = self.create_enhanced_comparison_summary()
        if summary is not None:
            summary.to_csv("results/enhanced_algorithm_comparison.csv", index=False)
            print("Enhanced summary saved to results/enhanced_algorithm_comparison.csv")
    
    def create_quick_visualization(self):
        """Create quick visualization of key metrics"""
        if not self.results:
            return
        
        summary = self.create_enhanced_comparison_summary()
        if summary is None:
            return
        
        # Create quick comparison plot
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        algorithms = summary['Algorithm']
        
        # Colors for different types
        colors = []
        for alg in algorithms:
            if 'AI' in alg or 'Hybrid' in alg:
                colors.append('#FF6B6B')  # Red for AI
            elif 'LB' in alg or 'Adaptive' in alg:
                colors.append('#4ECDC4')  # Teal for load balancing
            elif alg == 'Worst-Fit':
                colors.append('#45B7D1')  # Blue for best traditional
            else:
                colors.append('#96CEB4')  # Green for traditional
        
        # 1. Energy Consumption
        if 'total_energy_consumption_mean' in summary.columns:
            ax1 = axes[0, 0]
            energy_means = summary['total_energy_consumption_mean']
            energy_stds = summary.get('total_energy_consumption_std', [0]*len(algorithms))
            
            bars1 = ax1.bar(range(len(algorithms)), energy_means, yerr=energy_stds,
                           color=colors, alpha=0.8, capsize=5)
            ax1.set_title('Energy Consumption (Watts)', fontweight='bold')
            ax1.set_ylabel('Watts')
            ax1.set_xticks(range(len(algorithms)))
            ax1.set_xticklabels(algorithms, rotation=45, ha='right')
        
        # 2. Cost
        if 'total_cost_mean' in summary.columns:
            ax2 = axes[0, 1]
            cost_means = summary['total_cost_mean']
            cost_stds = summary.get('total_cost_std', [0]*len(algorithms))
            
            bars2 = ax2.bar(range(len(algorithms)), cost_means, yerr=cost_stds,
                           color=colors, alpha=0.8, capsize=5)
            ax2.set_title('Total Cost ($)', fontweight='bold')
            ax2.set_ylabel('Dollars')
            ax2.set_xticks(range(len(algorithms)))
            ax2.set_xticklabels(algorithms, rotation=45, ha='right')
        
        # 3. CPU vs RAM Utilization
        if 'average_cpu_utilization_mean' in summary.columns:
            ax3 = axes[1, 0]
            cpu_means = summary['average_cpu_utilization_mean'] * 100
            ram_means = summary['average_ram_utilization_mean'] * 100
            
            scatter3 = ax3.scatter(cpu_means, ram_means, c=colors, s=100, alpha=0.7)
            ax3.set_xlabel('CPU Utilization (%)')
            ax3.set_ylabel('RAM Utilization (%)')
            ax3.set_title('Resource Utilization Balance', fontweight='bold')
            ax3.axhline(y=70, color='red', linestyle='--', alpha=0.7)
            ax3.axvline(x=70, color='red', linestyle='--', alpha=0.7)
            
            # Add algorithm labels
            for i, alg in enumerate(algorithms):
                ax3.annotate(alg[:8], (cpu_means.iloc[i], ram_means.iloc[i]), 
                            xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # 4. Load Balancing vs Performance
        if 'cpu_load_balancing_index_mean' in summary.columns:
            ax4 = axes[1, 1]
            lb_index = (summary['cpu_load_balancing_index_mean'] + 
                       summary['ram_load_balancing_index_mean']) / 2
            
            # Calculate efficiency score
            energy_means = summary['total_energy_consumption_mean']
            cost_means = summary['total_cost_mean']
            efficiency = []
            for i in range(len(algorithms)):
                energy_norm = 1 - (energy_means.iloc[i] / energy_means.max())
                cost_norm = 1 - (cost_means.iloc[i] / cost_means.max())
                efficiency.append((energy_norm + cost_norm) / 2)
            
            scatter4 = ax4.scatter(lb_index, efficiency, c=colors, s=100, alpha=0.7)
            ax4.set_xlabel('Load Balance Index (Lower = Better)')
            ax4.set_ylabel('Performance Efficiency (Higher = Better)')
            ax4.set_title('Load Balance vs Performance', fontweight='bold')
            
            # Add algorithm labels
            for i, alg in enumerate(algorithms):
                ax4.annotate(alg[:8], (lb_index.iloc[i], efficiency[i]), 
                            xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('results/enhanced_quick_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """Main enhanced simulation function"""
    print("Enhanced VM Placement Algorithm Evaluation System")
    print("="*60)
    
    # Initialize enhanced simulator
    simulator = EnhancedVMPlacementSimulator()
    
    # Run comprehensive enhanced evaluation
    results = simulator.run_comprehensive_enhanced_evaluation(num_vm_requests=1000, num_runs=3)
    
    # Print enhanced results
    simulator.print_enhanced_results_summary()
    
    # Create quick visualization
    simulator.create_quick_visualization()
    
    # Save enhanced results
    simulator.save_enhanced_results()
    
    return simulator

if __name__ == "__main__":
    main()