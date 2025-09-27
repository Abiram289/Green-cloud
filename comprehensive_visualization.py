#!/usr/bin/env python3
"""
Comprehensive High-Level Visualization Suite for VM Placement Algorithms
Creates actionable insights, not just pretty charts
"""

import sys
import os
sys.path.append('src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
import json
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Import our algorithms
try:
    from src.improved_ai_algorithm import ImprovedAIPlacement
    from src.enhanced_algorithms import LoadBalancingBestFit, LoadBalancingFirstFit
    from src.placement_algorithms import FirstFitPlacement, RoundRobinPlacement, BestFitPlacement, WorstFitPlacement
    from src.data_generator import DataGenerator
except ImportError:
    # Fallback for running from different directory
    from improved_ai_algorithm import ImprovedAIPlacement
    from enhanced_algorithms import LoadBalancingBestFit, LoadBalancingFirstFit
    from placement_algorithms import FirstFitPlacement, RoundRobinPlacement, BestFitPlacement, WorstFitPlacement
    from data_generator import DataGenerator

class ComprehensiveVisualization:
    """
    High-level visualization suite that provides actionable insights
    for VM placement algorithm performance and decision-making
    """
    
    def __init__(self):
        self.colors = {
            'improved_ai': '#2E8B57',      # Sea Green - Best performing
            'original_ai': '#DC143C',      # Crimson - Worst performing  
            'best_fit': '#4682B4',         # Steel Blue
            'worst_fit': '#DAA520',        # Golden Rod
            'first_fit': '#8A2BE2',        # Blue Violet
            'round_robin': '#FF6347',      # Tomato
            'lb_best_fit': '#20B2AA',      # Light Sea Green
            'lb_first_fit': '#FF69B4'      # Hot Pink
        }
        
        # Set style for professional presentations
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
        
    def run_comprehensive_benchmark(self, num_scenarios: int = 100) -> Dict:
        """Run comprehensive benchmark across all algorithms"""
        print(f"🔄 Running comprehensive benchmark with {num_scenarios} scenarios...")
        
        # Initialize algorithms
        algorithms = {
            'Improved AI': ImprovedAIPlacement(),
            'LB-Best-Fit': LoadBalancingBestFit(),
            'LB-First-Fit': LoadBalancingFirstFit(), 
            'Round-Robin': RoundRobinPlacement(),
            'Best-Fit': BestFitPlacement(),
            'First-Fit': FirstFitPlacement(),
            'Worst-Fit': WorstFitPlacement()
        }
        
        # Generate test scenarios
        data_gen = DataGenerator(num_hosts=20, seed=42)
        results = {name: {
            'energy_consumption': [],
            'cost': [],
            'success_count': 0,
            'placement_times': [],
            'cpu_utilization': [],
            'ram_utilization': [],
            'load_balance_scores': [],
            'sla_violations': [],
            'efficiency_scores': []
        } for name in algorithms.keys()}
        
        print("Running scenarios...")
        for i in range(num_scenarios):
            if i % 20 == 0:
                print(f"  Progress: {i}/{num_scenarios}")
                
            scenario = data_gen.generate_scenario()
            vm_request = scenario['vm_request']
            hosts = [h.copy() for h in data_gen.host_specs]  # Fresh host states
            
            for algo_name, algorithm in algorithms.items():
                start_time = pd.Timestamp.now()
                
                try:
                    if hasattr(algorithm, 'place_vm_fixed'):
                        placement_id = algorithm.place_vm_fixed(vm_request, hosts)
                    else:
                        placement_id = algorithm.place_vm(vm_request, hosts)
                    
                    end_time = pd.Timestamp.now()
                    placement_time = (end_time - start_time).total_seconds() * 1000  # ms
                    
                    if placement_id != -1:
                        results[algo_name]['success_count'] += 1
                        selected_host = hosts[placement_id]
                        
                        # Calculate comprehensive metrics
                        if hasattr(algorithm, 'calculate_energy_consumption'):
                            energy = algorithm.calculate_energy_consumption(vm_request, selected_host)
                            cost = algorithm.calculate_cost(vm_request, selected_host)
                        else:
                            # Fallback calculations for basic algorithms
                            cpu_util_after = (selected_host["current_cpu_usage"] + vm_request["cpu_required"]) / selected_host["cpu_cores"]
                            energy = selected_host["base_power_watts"] * (0.3 + 0.7 * (cpu_util_after ** 1.3))
                            usage_factor = 1 + 0.5 * cpu_util_after
                            cost = selected_host["cost_per_hour"] * usage_factor * vm_request.get("expected_runtime_hours", 24)
                        
                        cpu_util = (selected_host["current_cpu_usage"] + vm_request["cpu_required"]) / selected_host["cpu_cores"]
                        ram_util = (selected_host["current_ram_usage"] + vm_request["ram_required"]) / selected_host["ram_gb"]
                        
                        # Load balance score (variance-based)
                        loads = [(h["current_cpu_usage"]/h["cpu_cores"] + h["current_ram_usage"]/h["ram_gb"])/2 for h in hosts]
                        load_balance_score = 1 - np.var(loads)  # Lower variance = better balance
                        
                        # SLA violation risk
                        sla_risk = max(0, cpu_util - 0.8) * 0.1 + max(0, ram_util - 0.8) * 0.1
                        
                        # Efficiency score (how close to optimal 70% utilization)
                        efficiency = 1 - abs((cpu_util + ram_util)/2 - 0.7)
                        
                        # Store results
                        results[algo_name]['energy_consumption'].append(energy)
                        results[algo_name]['cost'].append(cost)
                        results[algo_name]['placement_times'].append(placement_time)
                        results[algo_name]['cpu_utilization'].append(cpu_util)
                        results[algo_name]['ram_utilization'].append(ram_util)
                        results[algo_name]['load_balance_scores'].append(load_balance_score)
                        results[algo_name]['sla_violations'].append(sla_risk)
                        results[algo_name]['efficiency_scores'].append(efficiency)
                        
                except Exception as e:
                    # Algorithm failed
                    results[algo_name]['placement_times'].append(float('inf'))
        
        print("✅ Benchmark completed!")
        return results
    
    def create_executive_dashboard(self, results: Dict, save_path: str = "results/executive_dashboard.png"):
        """Create executive-level dashboard showing key business metrics"""
        
        fig = plt.figure(figsize=(20, 12))
        fig.suptitle('🏢 VM PLACEMENT ALGORITHMS - EXECUTIVE DASHBOARD\nKey Business Metrics & Performance Comparison', 
                     fontsize=20, fontweight='bold', y=0.95)
        
        # Calculate summary metrics
        summary_data = []
        for algo_name, data in results.items():
            if data['success_count'] > 0:
                avg_energy = np.mean(data['energy_consumption']) if data['energy_consumption'] else 0
                avg_cost = np.mean(data['cost']) if data['cost'] else 0
                success_rate = data['success_count'] / len([x for x in data['placement_times'] if x != float('inf')]) * 100
                avg_efficiency = np.mean(data['efficiency_scores']) if data['efficiency_scores'] else 0
                
                summary_data.append({
                    'Algorithm': algo_name,
                    'Avg Energy (W)': avg_energy,
                    'Avg Cost ($)': avg_cost,
                    'Success Rate (%)': success_rate,
                    'Efficiency Score': avg_efficiency
                })
        
        df_summary = pd.DataFrame(summary_data)
        
        # 1. ROI Impact Analysis (Top Left)
        ax1 = plt.subplot(2, 3, 1)
        cost_data = df_summary['Avg Cost ($)'].values
        energy_data = df_summary['Avg Energy (W)'].values
        colors = [self.colors.get(algo.lower().replace('-', '_').replace(' ', '_'), '#666666') for algo in df_summary['Algorithm']]
        
        scatter = ax1.scatter(cost_data, energy_data, s=200, c=colors, alpha=0.7, edgecolors='black')
        ax1.set_xlabel('Average Cost per VM ($)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Energy Consumption (W)', fontsize=12, fontweight='bold')
        ax1.set_title('💰 ROI IMPACT MATRIX\nLower = Better Performance', fontsize=14, fontweight='bold')
        
        # Add algorithm labels
        for i, algo in enumerate(df_summary['Algorithm']):
            ax1.annotate(algo, (cost_data[i], energy_data[i]), xytext=(5, 5), 
                        textcoords='offset points', fontsize=10, fontweight='bold')
        
        # Add ROI zones
        ax1.axhspan(0, np.percentile(energy_data, 25), alpha=0.1, color='green', label='High ROI Zone')
        ax1.axvspan(0, np.percentile(cost_data, 25), alpha=0.1, color='green')
        ax1.grid(True, alpha=0.3)
        
        # 2. Success Rate Comparison (Top Middle)
        ax2 = plt.subplot(2, 3, 2)
        success_rates = df_summary['Success Rate (%)'].values
        algo_names = [name[:10] + '...' if len(name) > 10 else name for name in df_summary['Algorithm']]
        
        bars = ax2.bar(range(len(algo_names)), success_rates, 
                      color=[self.colors.get(algo.lower().replace('-', '_').replace(' ', '_'), '#666666') for algo in df_summary['Algorithm']])
        ax2.set_xlabel('Algorithms', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Success Rate (%)', fontsize=12, fontweight='bold')
        ax2.set_title('✅ RELIABILITY ANALYSIS\nPlacement Success Rates', fontsize=14, fontweight='bold')
        ax2.set_xticks(range(len(algo_names)))
        ax2.set_xticklabels(algo_names, rotation=45, ha='right')
        ax2.set_ylim(0, 105)
        
        # Add value labels on bars
        for bar, rate in zip(bars, success_rates):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Add benchmark line
        ax2.axhline(y=95, color='red', linestyle='--', alpha=0.7, label='Target: 95%')
        ax2.legend()
        
        # 3. Efficiency vs Cost Trade-off (Top Right)
        ax3 = plt.subplot(2, 3, 3)
        efficiency_data = df_summary['Efficiency Score'].values
        
        for i, (eff, cost, algo) in enumerate(zip(efficiency_data, cost_data, df_summary['Algorithm'])):
            color = self.colors.get(algo.lower().replace('-', '_').replace(' ', '_'), '#666666')
            ax3.scatter(cost, eff, s=200, c=color, alpha=0.7, edgecolors='black')
            ax3.annotate(algo, (cost, eff), xytext=(5, 5), 
                        textcoords='offset points', fontsize=10, fontweight='bold')
        
        ax3.set_xlabel('Average Cost per VM ($)', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Efficiency Score', fontsize=12, fontweight='bold')
        ax3.set_title('⚡ EFFICIENCY vs COST TRADE-OFF\nHigher Efficiency, Lower Cost = Better', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Add optimal zone
        if len(efficiency_data) > 1:
            best_eff = np.max(efficiency_data)
            best_cost = np.min(cost_data)
            ax3.axhspan(best_eff * 0.9, best_eff * 1.1, alpha=0.1, color='green', label='Optimal Zone')
            ax3.axvspan(0, best_cost * 1.5, alpha=0.1, color='green')
        
        # 4. Resource Utilization Patterns (Bottom Left)
        ax4 = plt.subplot(2, 3, 4)
        
        utilization_data = []
        for algo_name, data in results.items():
            if data['cpu_utilization'] and data['ram_utilization']:
                avg_cpu = np.mean(data['cpu_utilization']) * 100
                avg_ram = np.mean(data['ram_utilization']) * 100
                utilization_data.append([avg_cpu, avg_ram])
            else:
                utilization_data.append([0, 0])
        
        utilization_array = np.array(utilization_data)
        x = np.arange(len(df_summary['Algorithm']))
        width = 0.35
        
        bars1 = ax4.bar(x - width/2, utilization_array[:, 0], width, label='CPU Utilization', 
                       alpha=0.8, color='skyblue')
        bars2 = ax4.bar(x + width/2, utilization_array[:, 1], width, label='RAM Utilization', 
                       alpha=0.8, color='lightcoral')
        
        ax4.set_xlabel('Algorithms', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Average Utilization (%)', fontsize=12, fontweight='bold')
        ax4.set_title('📊 RESOURCE UTILIZATION PATTERNS\nOptimal Range: 60-80%', fontsize=14, fontweight='bold')
        ax4.set_xticks(x)
        ax4.set_xticklabels([name[:10] + '...' if len(name) > 10 else name for name in df_summary['Algorithm']], 
                           rotation=45, ha='right')
        ax4.legend()
        
        # Add optimal zones
        ax4.axhspan(60, 80, alpha=0.2, color='green', label='Optimal Zone')
        ax4.axhspan(80, 100, alpha=0.1, color='orange', label='High Risk Zone')
        
        # 5. Performance Ranking Matrix (Bottom Middle)
        ax5 = plt.subplot(2, 3, 5)
        
        # Calculate normalized scores (0-1 scale, higher is better)
        norm_success = success_rates / 100
        norm_efficiency = efficiency_data
        norm_cost = 1 - (cost_data - np.min(cost_data)) / (np.max(cost_data) - np.min(cost_data) + 1e-6)
        norm_energy = 1 - (energy_data - np.min(energy_data)) / (np.max(energy_data) - np.min(energy_data) + 1e-6)
        
        # Weighted composite score
        composite_scores = (0.3 * norm_success + 0.25 * norm_efficiency + 
                           0.25 * norm_cost + 0.2 * norm_energy)
        
        # Create ranking
        ranking_data = pd.DataFrame({
            'Algorithm': df_summary['Algorithm'],
            'Composite Score': composite_scores,
            'Success': norm_success,
            'Efficiency': norm_efficiency,
            'Cost': norm_cost,
            'Energy': norm_energy
        }).sort_values('Composite Score', ascending=False)
        
        # Create heatmap
        heatmap_data = ranking_data[['Success', 'Efficiency', 'Cost', 'Energy']].values
        im = ax5.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        ax5.set_xticks(range(4))
        ax5.set_xticklabels(['Success', 'Efficiency', 'Cost', 'Energy'], fontweight='bold')
        ax5.set_yticks(range(len(ranking_data)))
        ax5.set_yticklabels([f"#{i+1} {name}" for i, name in enumerate(ranking_data['Algorithm'])], 
                           fontweight='bold')
        ax5.set_title('🏆 OVERALL PERFORMANCE RANKING\nGreen = Better, Red = Worse', fontsize=14, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax5, shrink=0.8)
        cbar.set_label('Normalized Score', fontweight='bold')
        
        # 6. Executive Summary Table (Bottom Right)
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        
        # Create summary table using DataFrame lookups (avoid boolean indexing on numpy arrays)
        best_algo = ranking_data.iloc[0]['Algorithm']
        worst_algo = ranking_data.iloc[-1]['Algorithm']
        
        best_row = df_summary[df_summary['Algorithm'] == best_algo].iloc[0]
        worst_row = df_summary[df_summary['Algorithm'] == worst_algo].iloc[0]
        
        best_success = best_row['Success Rate (%)']
        best_cost = best_row['Avg Cost ($)']
        best_energy = best_row['Avg Energy (W)']
        
        worst_success = worst_row['Success Rate (%)']
        worst_cost = worst_row['Avg Cost ($)']
        worst_energy = worst_row['Avg Energy (W)']
        
        summary_text = f"""
📋 EXECUTIVE SUMMARY

🏆 TOP PERFORMER: {best_algo}
• Score: {ranking_data.iloc[0]['Composite Score']:.3f}
• Success Rate: {best_success:.1f}%
• Avg Cost: ${best_cost:.0f}
• Avg Energy: {best_energy:.0f}W

❌ LOWEST PERFORMER: {worst_algo}
• Score: {ranking_data.iloc[-1]['Composite Score']:.3f}
• Success Rate: {worst_success:.1f}%
• Avg Cost: ${worst_cost:.0f}
• Avg Energy: {worst_energy:.0f}W

📊 KEY INSIGHTS:
• Cost Savings: Up to {((np.max(cost_data) - np.min(cost_data)) / (np.max(cost_data) + 1e-6) * 100):.0f}% reduction possible
• Energy Savings: Up to {((np.max(energy_data) - np.min(energy_data)) / (np.max(energy_data) + 1e-6) * 100):.0f}% reduction possible
• Best ROI: Choose {best_algo} for optimal performance

💡 RECOMMENDATION:
Deploy {best_algo} for production workloads
        """
        
        ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        plt.tight_layout()
        
        # Save with high DPI for presentations
        os.makedirs('results', exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"📊 Executive dashboard saved to: {save_path}")
        
        return ranking_data
    
    def create_technical_deep_dive(self, results: Dict, save_path: str = "results/technical_analysis.png"):
        """Create technical deep-dive visualization for engineers and architects"""
        
        fig = plt.figure(figsize=(24, 16))
        fig.suptitle('🔧 VM PLACEMENT ALGORITHMS - TECHNICAL DEEP DIVE\nPerformance Analysis & System Optimization Insights', 
                     fontsize=22, fontweight='bold', y=0.96)
        
        # 1. Algorithm Performance Distribution (Top Left)
        ax1 = plt.subplot(3, 4, 1)
        
        energy_distributions = []
        labels = []
        colors_list = []
        
        for algo_name, data in results.items():
            if data['energy_consumption']:
                energy_distributions.append(data['energy_consumption'])
                labels.append(algo_name)
                colors_list.append(self.colors.get(algo_name.lower().replace('-', '_').replace(' ', '_'), '#666666'))
        
        parts = ax1.violinplot(energy_distributions, positions=range(len(labels)), showmeans=True, showmedians=True)
        
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(colors_list[i])
            pc.set_alpha(0.7)
        
        ax1.set_xlabel('Algorithms', fontweight='bold')
        ax1.set_ylabel('Energy Consumption (W)', fontweight='bold')
        ax1.set_title('⚡ ENERGY DISTRIBUTION ANALYSIS\nViolin Plot Shows Full Distribution', fontweight='bold')
        ax1.set_xticks(range(len(labels)))
        ax1.set_xticklabels([label[:8] + '...' if len(label) > 8 else label for label in labels], rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        
        # 2. Cost vs Energy Efficiency Frontier (Top Middle-Left)
        ax2 = plt.subplot(3, 4, 2)
        
        for algo_name, data in results.items():
            if data['energy_consumption'] and data['cost']:
                avg_energy = np.mean(data['energy_consumption'])
                avg_cost = np.mean(data['cost'])
                std_energy = np.std(data['energy_consumption'])
                std_cost = np.std(data['cost'])
                
                color = self.colors.get(algo_name.lower().replace('-', '_').replace(' ', '_'), '#666666')
                ax2.errorbar(avg_energy, avg_cost, xerr=std_energy, yerr=std_cost, 
                           fmt='o', color=color, markersize=10, capsize=5, alpha=0.8, label=algo_name)
        
        ax2.set_xlabel('Average Energy Consumption (W)', fontweight='bold')
        ax2.set_ylabel('Average Cost ($)', fontweight='bold')
        ax2.set_title('💰 COST-ENERGY EFFICIENCY FRONTIER\nError Bars Show Variability', fontweight='bold')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # 3. Resource Utilization Heatmap (Top Middle-Right)
        ax3 = plt.subplot(3, 4, 3)
        
        utilization_matrix = []
        util_labels = []
        
        for algo_name, data in results.items():
            if data['cpu_utilization'] and data['ram_utilization']:
                cpu_utils = np.array(data['cpu_utilization']) * 100
                ram_utils = np.array(data['ram_utilization']) * 100
                
                utilization_matrix.append([
                    np.mean(cpu_utils),
                    np.std(cpu_utils),
                    np.mean(ram_utils),
                    np.std(ram_utils),
                    np.mean(np.abs(cpu_utils - ram_utils))  # Balance score
                ])
                util_labels.append(algo_name)
        
        if utilization_matrix:
            util_array = np.array(utilization_matrix)
            im3 = ax3.imshow(util_array, cmap='viridis', aspect='auto')
            
            ax3.set_xticks(range(5))
            ax3.set_xticklabels(['CPU Avg', 'CPU Std', 'RAM Avg', 'RAM Std', 'Imbalance'], rotation=45, ha='right')
            ax3.set_yticks(range(len(util_labels)))
            ax3.set_yticklabels(util_labels)
            ax3.set_title('📊 RESOURCE UTILIZATION HEATMAP\nDarker = Higher Values', fontweight='bold')
            
            # Add text annotations
            for i in range(len(util_labels)):
                for j in range(5):
                    text = ax3.text(j, i, f'{util_array[i, j]:.1f}', 
                                  ha="center", va="center", color="white" if util_array[i, j] > np.mean(util_array) else "black")
            
            plt.colorbar(im3, ax=ax3, shrink=0.6)
        
        # 4. Load Balancing Performance (Top Right)
        ax4 = plt.subplot(3, 4, 4)
        
        balance_data = []
        balance_labels = []
        
        for algo_name, data in results.items():
            if data['load_balance_scores']:
                balance_scores = np.array(data['load_balance_scores'])
                balance_data.append(balance_scores)
                balance_labels.append(algo_name)
        
        if balance_data:
            bp = ax4.boxplot(balance_data, labels=[label[:8] + '...' if len(label) > 8 else label for label in balance_labels], 
                            patch_artist=True)
            
            for patch, label in zip(bp['boxes'], balance_labels):
                color = self.colors.get(label.lower().replace('-', '_').replace(' ', '_'), '#666666')
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
        
        ax4.set_xlabel('Algorithms', fontweight='bold')
        ax4.set_ylabel('Load Balance Score', fontweight='bold')
        ax4.set_title('⚖️ LOAD BALANCING PERFORMANCE\nHigher = Better Balance', fontweight='bold')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
        
        # 5. Response Time Analysis (Middle Left)
        ax5 = plt.subplot(3, 4, 5)
        
        time_data = []
        time_labels = []
        
        for algo_name, data in results.items():
            valid_times = [t for t in data['placement_times'] if t != float('inf')]
            if valid_times:
                time_data.append(valid_times)
                time_labels.append(algo_name)
        
        if time_data:
            # Create histogram overlay
            for i, (times, label) in enumerate(zip(time_data, time_labels)):
                color = self.colors.get(label.lower().replace('-', '_').replace(' ', '_'), '#666666')
                ax5.hist(times, bins=20, alpha=0.6, label=label, color=color, density=True)
        
        ax5.set_xlabel('Placement Time (ms)', fontweight='bold')
        ax5.set_ylabel('Density', fontweight='bold')
        ax5.set_title('⏱️ RESPONSE TIME DISTRIBUTION\nFaster = Better User Experience', fontweight='bold')
        ax5.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax5.grid(True, alpha=0.3)
        
        # 6. SLA Violation Risk Analysis (Middle Middle-Left)
        ax6 = plt.subplot(3, 4, 6)
        
        sla_data = []
        sla_labels = []
        
        for algo_name, data in results.items():
            if data['sla_violations']:
                sla_violations = np.array(data['sla_violations']) * 100  # Convert to percentage
                sla_data.append(sla_violations)
                sla_labels.append(algo_name)
        
        if sla_data:
            # Create stacked bar chart showing risk levels
            low_risk = []
            medium_risk = []
            high_risk = []
            
            for violations in sla_data:
                low_risk.append(np.sum(violations < 2))
                medium_risk.append(np.sum((violations >= 2) & (violations < 5)))
                high_risk.append(np.sum(violations >= 5))
            
            x = np.arange(len(sla_labels))
            width = 0.6
            
            p1 = ax6.bar(x, low_risk, width, label='Low Risk (<2%)', color='green', alpha=0.7)
            p2 = ax6.bar(x, medium_risk, width, bottom=low_risk, label='Medium Risk (2-5%)', color='orange', alpha=0.7)
            p3 = ax6.bar(x, high_risk, width, bottom=np.array(low_risk) + np.array(medium_risk), 
                        label='High Risk (>5%)', color='red', alpha=0.7)
            
            ax6.set_xlabel('Algorithms', fontweight='bold')
            ax6.set_ylabel('Number of Placements', fontweight='bold')
            ax6.set_title('⚠️ SLA VIOLATION RISK ANALYSIS\nGreen = Safe, Red = Risky', fontweight='bold')
            ax6.set_xticks(x)
            ax6.set_xticklabels([label[:8] + '...' if len(label) > 8 else label for label in sla_labels], rotation=45, ha='right')
            ax6.legend()
        
        # 7. Algorithm Scalability Analysis (Middle Middle-Right)
        ax7 = plt.subplot(3, 4, 7)
        
        # Simulate scalability by analyzing performance vs complexity
        complexity_metrics = []
        performance_metrics = []
        scalability_labels = []
        
        for algo_name, data in results.items():
            if data['energy_consumption'] and data['placement_times']:
                # Complexity proxy: average response time
                avg_time = np.mean([t for t in data['placement_times'] if t != float('inf')])
                # Performance proxy: composite efficiency
                avg_energy = np.mean(data['energy_consumption'])
                avg_efficiency = np.mean(data['efficiency_scores']) if data['efficiency_scores'] else 0
                
                complexity_metrics.append(avg_time)
                performance_metrics.append(avg_efficiency)
                scalability_labels.append(algo_name)
        
        if complexity_metrics and performance_metrics:
            for i, label in enumerate(scalability_labels):
                color = self.colors.get(label.lower().replace('-', '_').replace(' ', '_'), '#666666')
                ax7.scatter(complexity_metrics[i], performance_metrics[i], 
                          s=200, c=color, alpha=0.7, edgecolors='black')
                ax7.annotate(label, (complexity_metrics[i], performance_metrics[i]), 
                           xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        ax7.set_xlabel('Average Response Time (ms) - Complexity', fontweight='bold')
        ax7.set_ylabel('Average Efficiency Score - Performance', fontweight='bold')
        ax7.set_title('📈 SCALABILITY ANALYSIS\nTop-Left = Best (Fast & Efficient)', fontweight='bold')
        ax7.grid(True, alpha=0.3)
        
        # 8. Resource Efficiency Radar Chart (Middle Right)
        ax8 = plt.subplot(3, 4, 8, projection='polar')
        
        # Prepare radar chart data
        metrics = ['Energy Eff.', 'Cost Eff.', 'CPU Util.', 'RAM Util.', 'Load Balance', 'SLA Safety']
        
        for algo_name, data in results.items():
            if (data['energy_consumption'] and data['cost'] and 
                data['cpu_utilization'] and data['ram_utilization'] and
                data['load_balance_scores'] and data['sla_violations']):
                
                # Normalize all metrics to 0-1 scale
                energy_eff = 1 - (np.mean(data['energy_consumption']) - 50) / 500  # Assume 50-550W range
                cost_eff = 1 - (np.mean(data['cost']) - 10) / 200  # Assume $10-210 range
                cpu_util = 1 - abs(np.mean(data['cpu_utilization']) - 0.7) / 0.3  # Optimal around 70%
                ram_util = 1 - abs(np.mean(data['ram_utilization']) - 0.7) / 0.3
                load_balance = np.mean(data['load_balance_scores'])
                sla_safety = 1 - np.mean(data['sla_violations'])
                
                values = [energy_eff, cost_eff, cpu_util, ram_util, load_balance, sla_safety]
                values = [max(0, min(1, v)) for v in values]  # Clamp to 0-1
                values += values[:1]  # Close the polygon
                
                angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
                angles += angles[:1]
                
                color = self.colors.get(algo_name.lower().replace('-', '_').replace(' ', '_'), '#666666')
                ax8.plot(angles, values, 'o-', linewidth=2, label=algo_name, color=color, alpha=0.8)
                ax8.fill(angles, values, alpha=0.1, color=color)
        
        ax8.set_xticks(np.linspace(0, 2 * np.pi, len(metrics), endpoint=False))
        ax8.set_xticklabels(metrics)
        ax8.set_ylim(0, 1)
        ax8.set_title('🎯 MULTI-DIMENSIONAL PERFORMANCE\nLarger Area = Better Overall', fontweight='bold', pad=20)
        ax8.legend(bbox_to_anchor=(1.3, 1), loc='upper left', fontsize=8)
        ax8.grid(True)
        
        # 9-12. Algorithm-Specific Insights (Bottom Row)
        bottom_axes = [plt.subplot(3, 4, i) for i in range(9, 13)]
        
        # Get top 4 algorithms by performance
        algo_performance = []
        for algo_name, data in results.items():
            if data['energy_consumption'] and data['cost']:
                avg_energy = np.mean(data['energy_consumption'])
                avg_cost = np.mean(data['cost'])
                success_rate = data['success_count'] / len([t for t in data['placement_times'] if t != float('inf')])
                composite_score = success_rate * 0.4 + (1/(avg_energy+1)) * 0.3 + (1/(avg_cost+1)) * 0.3
                algo_performance.append((algo_name, composite_score, data))
        
        algo_performance.sort(key=lambda x: x[1], reverse=True)
        
        for i, (ax, (algo_name, score, data)) in enumerate(zip(bottom_axes, algo_performance[:4])):
            # Create individual algorithm performance breakdown
            categories = ['Success\nRate', 'Energy\nEfficiency', 'Cost\nEfficiency', 'Response\nTime']
            
            success_score = data['success_count'] / len([t for t in data['placement_times'] if t != float('inf')]) * 100
            energy_score = 100 - (np.mean(data['energy_consumption']) - 50) / 5  # Rough normalization
            cost_score = 100 - (np.mean(data['cost']) - 10) / 2  # Rough normalization
            time_score = 100 - np.mean([t for t in data['placement_times'] if t != float('inf')])
            
            scores = [max(0, min(100, s)) for s in [success_score, energy_score, cost_score, time_score]]
            
            color = self.colors.get(algo_name.lower().replace('-', '_').replace(' ', '_'), '#666666')
            bars = ax.bar(categories, scores, color=color, alpha=0.7)
            
            ax.set_ylabel('Score (0-100)', fontweight='bold')
            ax.set_title(f'📋 {algo_name.upper()}\nDetailed Performance', fontweight='bold', fontsize=10)
            ax.set_ylim(0, 105)
            
            # Add score labels
            for bar, score in zip(bars, scores):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                       f'{score:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
            
            ax.tick_params(axis='x', labelsize=8)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save high-resolution version
        os.makedirs('results', exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"🔧 Technical analysis saved to: {save_path}")
    
    def create_algorithm_comparison_matrix(self, results: Dict, save_path: str = "results/comparison_matrix.png"):
        """Create comprehensive algorithm comparison matrix"""
        
        fig, ax = plt.subplots(figsize=(16, 10))
        fig.suptitle('🔍 ALGORITHM COMPARISON MATRIX\nComprehensive Performance Analysis', 
                     fontsize=18, fontweight='bold')
        
        # Prepare comparison data
        comparison_data = []
        algo_names = []
        
        metrics = ['Success Rate (%)', 'Avg Energy (W)', 'Avg Cost ($)', 'Avg Response (ms)', 
                  'CPU Utilization (%)', 'RAM Utilization (%)', 'Load Balance Score', 'SLA Safety Score']
        
        for algo_name, data in results.items():
            if data['success_count'] > 0:
                row_data = []
                
                # Success Rate
                success_rate = (data['success_count'] / len([t for t in data['placement_times'] if t != float('inf')])) * 100
                row_data.append(success_rate)
                
                # Average Energy
                avg_energy = np.mean(data['energy_consumption']) if data['energy_consumption'] else 0
                row_data.append(avg_energy)
                
                # Average Cost
                avg_cost = np.mean(data['cost']) if data['cost'] else 0
                row_data.append(avg_cost)
                
                # Average Response Time
                valid_times = [t for t in data['placement_times'] if t != float('inf')]
                avg_response = np.mean(valid_times) if valid_times else 0
                row_data.append(avg_response)
                
                # CPU Utilization
                avg_cpu = np.mean(data['cpu_utilization']) * 100 if data['cpu_utilization'] else 0
                row_data.append(avg_cpu)
                
                # RAM Utilization  
                avg_ram = np.mean(data['ram_utilization']) * 100 if data['ram_utilization'] else 0
                row_data.append(avg_ram)
                
                # Load Balance Score
                avg_balance = np.mean(data['load_balance_scores']) if data['load_balance_scores'] else 0
                row_data.append(avg_balance)
                
                # SLA Safety Score
                avg_sla_safety = 1 - np.mean(data['sla_violations']) if data['sla_violations'] else 0
                row_data.append(avg_sla_safety)
                
                comparison_data.append(row_data)
                algo_names.append(algo_name)
        
        # Create DataFrame
        df_comparison = pd.DataFrame(comparison_data, columns=metrics, index=algo_names)
        
        # Normalize data for better visualization (0-1 scale, higher is better)
        df_normalized = df_comparison.copy()
        
        # For metrics where lower is better, invert the scale
        for metric in ['Avg Energy (W)', 'Avg Cost ($)', 'Avg Response (ms)']:
            if metric in df_normalized.columns:
                col_data = df_normalized[metric]
                if col_data.max() != col_data.min():
                    df_normalized[metric] = 1 - (col_data - col_data.min()) / (col_data.max() - col_data.min())
                else:
                    df_normalized[metric] = 1.0
        
        # For other metrics, normalize directly (higher is better)
        for metric in ['Success Rate (%)', 'CPU Utilization (%)', 'RAM Utilization (%)', 'Load Balance Score', 'SLA Safety Score']:
            if metric in df_normalized.columns:
                col_data = df_normalized[metric]
                if col_data.max() != col_data.min():
                    df_normalized[metric] = (col_data - col_data.min()) / (col_data.max() - col_data.min())
                else:
                    df_normalized[metric] = 1.0
        
        # Create heatmap
        im = ax.imshow(df_normalized.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        # Set ticks and labels
        ax.set_xticks(range(len(metrics)))
        ax.set_xticklabels(metrics, rotation=45, ha='right', fontweight='bold')
        ax.set_yticks(range(len(algo_names)))
        ax.set_yticklabels(algo_names, fontweight='bold')
        
        # Add text annotations with actual values
        for i in range(len(algo_names)):
            for j in range(len(metrics)):
                actual_value = df_comparison.iloc[i, j]
                normalized_value = df_normalized.iloc[i, j]
                
                # Format the display value
                if 'Rate' in metrics[j] or 'Utilization' in metrics[j]:
                    display_text = f'{actual_value:.1f}%'
                elif 'Energy' in metrics[j]:
                    display_text = f'{actual_value:.0f}W'
                elif 'Cost' in metrics[j]:
                    display_text = f'${actual_value:.0f}'
                elif 'Response' in metrics[j]:
                    display_text = f'{actual_value:.1f}ms'
                else:
                    display_text = f'{actual_value:.3f}'
                
                # Choose text color based on background
                text_color = 'white' if normalized_value < 0.5 else 'black'
                
                ax.text(j, i, display_text, ha="center", va="center", 
                       color=text_color, fontweight='bold', fontsize=9)
        
        # Add colorbar
        cbar = fig.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('Normalized Performance Score\n(Green = Better, Red = Worse)', 
                      fontweight='bold', fontsize=12)
        
        # Add ranking
        composite_scores = df_normalized.mean(axis=1).sort_values(ascending=False)
        
        # Add ranking text
        ranking_text = "🏆 OVERALL RANKING:\n"
        for i, (algo, score) in enumerate(composite_scores.items()):
            ranking_text += f"#{i+1} {algo}: {score:.3f}\n"
        
        ax.text(1.15, 0.5, ranking_text, transform=ax.transAxes, fontsize=11,
               verticalalignment='center', fontfamily='monospace',
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"🔍 Comparison matrix saved to: {save_path}")
        
        return df_comparison
    
    def generate_all_visualizations(self, num_scenarios: int = 100):
        """Generate complete visualization suite"""
        print("🎨 Generating comprehensive visualization suite...")
        
        # Run benchmark
        results = self.run_comprehensive_benchmark(num_scenarios)
        
        # Generate all visualizations
        print("\n📊 Creating executive dashboard...")
        ranking = self.create_executive_dashboard(results)
        
        print("\n🔧 Creating technical deep dive...")
        self.create_technical_deep_dive(results)
        
        print("\n🔍 Creating comparison matrix...")
        comparison_df = self.create_algorithm_comparison_matrix(results)
        
        # Save raw results for further analysis
        with open('results/benchmark_results.json', 'w') as f:
            # Convert numpy arrays to lists for JSON serialization
            json_results = {}
            for algo, data in results.items():
                json_results[algo] = {
                    key: value.tolist() if isinstance(value, np.ndarray) else value
                    for key, value in data.items()
                }
            json.dump(json_results, f, indent=2)
        
        comparison_df.to_csv('results/algorithm_comparison.csv')
        ranking.to_csv('results/performance_ranking.csv')
        
        print("\n✅ Complete visualization suite generated!")
        print("📁 Files saved in 'results/' directory:")
        print("   • executive_dashboard.png - High-level business metrics")
        print("   • technical_analysis.png - Detailed technical analysis") 
        print("   • comparison_matrix.png - Algorithm comparison matrix")
        print("   • benchmark_results.json - Raw performance data")
        print("   • algorithm_comparison.csv - Comparison spreadsheet")
        print("   • performance_ranking.csv - Ranking spreadsheet")
        
        return results, ranking, comparison_df

def main():
    """Main function to generate all visualizations"""
    viz = ComprehensiveVisualization()
    results, ranking, comparison = viz.generate_all_visualizations(num_scenarios=50)  # Reduced for faster testing
    
    print("\n🎉 Visualization generation complete!")
    print(f"\n🏆 Top performing algorithm: {ranking.iloc[0]['Algorithm']}")
    print(f"📊 Performance score: {ranking.iloc[0]['Composite Score']:.3f}")
    
    return results, ranking, comparison

if __name__ == "__main__":
    main()