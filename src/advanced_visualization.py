"""
Advanced Visualization Suite for VM Placement Analysis

This module creates comprehensive visualizations including:
1. Detailed comparison charts for all metrics
2. Radar plots for multi-dimensional analysis
3. Load balancing visualizations
4. Performance heatmaps
5. Statistical analysis charts
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import json
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AdvancedVisualizationSuite:
    """Advanced visualization suite for VM placement analysis"""
    
    def __init__(self, results_path: str = "results/simulation_results.json"):
        """Initialize with simulation results"""
        self.results_path = results_path
        self.results = self.load_results()
        self.algorithms = list(self.results.keys()) if self.results else []
        
    def load_results(self) -> Dict:
        """Load simulation results"""
        try:
            with open(self.results_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Results file {self.results_path} not found. Please run simulation first.")
            return {}
    
    def create_comprehensive_comparison(self):
        """Create comprehensive comparison charts for all metrics"""
        if not self.results:
            print("No results available for visualization")
            return
        
        # Extract data for visualization
        algorithms = self.algorithms
        
        # Primary metrics
        energy_means = [self.results[alg]['total_energy_consumption_mean'] for alg in algorithms]
        energy_stds = [self.results[alg]['total_energy_consumption_std'] for alg in algorithms]
        
        cost_means = [self.results[alg]['total_cost_mean'] for alg in algorithms]
        cost_stds = [self.results[alg]['total_cost_std'] for alg in algorithms]
        
        cpu_means = [self.results[alg]['average_cpu_utilization_mean'] * 100 for alg in algorithms]
        cpu_stds = [self.results[alg]['average_cpu_utilization_std'] * 100 for alg in algorithms]
        
        ram_means = [self.results[alg]['average_ram_utilization_mean'] * 100 for alg in algorithms]
        ram_stds = [self.results[alg]['average_ram_utilization_std'] * 100 for alg in algorithms]
        
        sla_means = [self.results[alg]['sla_violations_mean'] for alg in algorithms]
        sla_stds = [self.results[alg]['sla_violations_std'] for alg in algorithms]
        
        success_means = [self.results[alg]['placement_success_rate_mean'] * 100 for alg in algorithms]
        success_stds = [self.results[alg]['placement_success_rate_std'] * 100 for alg in algorithms]
        
        # Create comprehensive figure
        fig = plt.figure(figsize=(20, 16))
        
        # Define color scheme - highlight AI algorithms
        colors = []
        for alg in algorithms:
            if 'AI' in alg or 'Hybrid' in alg:
                colors.append('#FF6B6B')  # Red for AI
            elif 'LB' in alg or 'Adaptive' in alg:
                colors.append('#4ECDC4')  # Teal for load balancing
            elif alg == 'Worst-Fit':
                colors.append('#45B7D1')  # Blue for best traditional performer
            else:
                colors.append('#96CEB4')  # Green for other traditional
        
        # 1. Energy Consumption
        ax1 = plt.subplot(3, 3, 1)
        bars1 = ax1.bar(range(len(algorithms)), energy_means, yerr=energy_stds, 
                       color=colors, alpha=0.8, capsize=5)
        ax1.set_title('Energy Consumption (Watts)', fontweight='bold', fontsize=12)
        ax1.set_ylabel('Watts')
        ax1.set_xticks(range(len(algorithms)))
        ax1.set_xticklabels(algorithms, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, mean in zip(bars1, energy_means):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(energy_stds)*0.1,
                    f'{int(mean)}', ha='center', va='bottom', fontsize=8)
        
        # 2. Total Cost
        ax2 = plt.subplot(3, 3, 2)
        bars2 = ax2.bar(range(len(algorithms)), cost_means, yerr=cost_stds,
                       color=colors, alpha=0.8, capsize=5)
        ax2.set_title('Total Cost ($)', fontweight='bold', fontsize=12)
        ax2.set_ylabel('Dollars')
        ax2.set_xticks(range(len(algorithms)))
        ax2.set_xticklabels(algorithms, rotation=45, ha='right')
        
        for bar, mean in zip(bars2, cost_means):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + max(cost_stds)*0.1,
                    f'{int(mean)}', ha='center', va='bottom', fontsize=8)
        
        # 3. CPU Utilization
        ax3 = plt.subplot(3, 3, 3)
        bars3 = ax3.bar(range(len(algorithms)), cpu_means, yerr=cpu_stds,
                       color=colors, alpha=0.8, capsize=5)
        ax3.set_title('Average CPU Utilization (%)', fontweight='bold', fontsize=12)
        ax3.set_ylabel('Percentage')
        ax3.set_xticks(range(len(algorithms)))
        ax3.set_xticklabels(algorithms, rotation=45, ha='right')
        ax3.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Target (70%)')
        ax3.legend()
        
        for bar, mean in zip(bars3, cpu_means):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + max(cpu_stds)*0.1,
                    f'{mean:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # 4. RAM Utilization
        ax4 = plt.subplot(3, 3, 4)
        bars4 = ax4.bar(range(len(algorithms)), ram_means, yerr=ram_stds,
                       color=colors, alpha=0.8, capsize=5)
        ax4.set_title('Average RAM Utilization (%)', fontweight='bold', fontsize=12)
        ax4.set_ylabel('Percentage')
        ax4.set_xticks(range(len(algorithms)))
        ax4.set_xticklabels(algorithms, rotation=45, ha='right')
        ax4.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Target (70%)')
        ax4.legend()
        
        for bar, mean in zip(bars4, ram_means):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + max(ram_stds)*0.1,
                    f'{mean:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # 5. SLA Violations
        ax5 = plt.subplot(3, 3, 5)
        bars5 = ax5.bar(range(len(algorithms)), sla_means, yerr=sla_stds,
                       color=colors, alpha=0.8, capsize=5)
        ax5.set_title('SLA Violations (Count)', fontweight='bold', fontsize=12)
        ax5.set_ylabel('Count')
        ax5.set_xticks(range(len(algorithms)))
        ax5.set_xticklabels(algorithms, rotation=45, ha='right')
        
        for bar, mean in zip(bars5, sla_means):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + max(sla_stds)*0.1,
                    f'{mean:.1f}', ha='center', va='bottom', fontsize=8)
        
        # 6. Success Rate
        ax6 = plt.subplot(3, 3, 6)
        bars6 = ax6.bar(range(len(algorithms)), success_means, yerr=success_stds,
                       color=colors, alpha=0.8, capsize=5)
        ax6.set_title('Placement Success Rate (%)', fontweight='bold', fontsize=12)
        ax6.set_ylabel('Percentage')
        ax6.set_xticks(range(len(algorithms)))
        ax6.set_xticklabels(algorithms, rotation=45, ha='right')
        
        for bar, mean in zip(bars6, success_means):
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height + max(success_stds)*0.1,
                    f'{mean:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # 7. Performance Efficiency Score
        ax7 = plt.subplot(3, 3, 7)
        efficiency_scores = []
        for alg in algorithms:
            # Calculate composite efficiency score
            energy_norm = 1 - (self.results[alg]['total_energy_consumption_mean'] / max(energy_means))
            cost_norm = 1 - (self.results[alg]['total_cost_mean'] / max(cost_means))
            cpu_eff = 1 - abs(self.results[alg]['average_cpu_utilization_mean'] - 0.7)
            ram_eff = 1 - abs(self.results[alg]['average_ram_utilization_mean'] - 0.7)
            sla_norm = 1 - (self.results[alg]['sla_violations_mean'] / max(sla_means)) if max(sla_means) > 0 else 1
            
            efficiency = (energy_norm + cost_norm + cpu_eff + ram_eff + sla_norm) / 5 * 100
            efficiency_scores.append(efficiency)
        
        bars7 = ax7.bar(range(len(algorithms)), efficiency_scores, color=colors, alpha=0.8)
        ax7.set_title('Overall Efficiency Score (%)', fontweight='bold', fontsize=12)
        ax7.set_ylabel('Efficiency %')
        ax7.set_xticks(range(len(algorithms)))
        ax7.set_xticklabels(algorithms, rotation=45, ha='right')
        
        for bar, score in zip(bars7, efficiency_scores):
            height = bar.get_height()
            ax7.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{score:.1f}%', ha='center', va='bottom', fontsize=8)
        
        # 8. Cost-Energy Trade-off
        ax8 = plt.subplot(3, 3, 8)
        scatter = ax8.scatter(energy_means, cost_means, c=colors, s=100, alpha=0.7)
        ax8.set_xlabel('Energy Consumption (Watts)')
        ax8.set_ylabel('Cost ($)')
        ax8.set_title('Cost vs Energy Trade-off', fontweight='bold', fontsize=12)
        
        # Add algorithm labels
        for i, alg in enumerate(algorithms):
            ax8.annotate(alg, (energy_means[i], cost_means[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # 9. Utilization Balance
        ax9 = plt.subplot(3, 3, 9)
        cpu_means_decimal = [x/100 for x in cpu_means]
        ram_means_decimal = [x/100 for x in ram_means]
        
        scatter9 = ax9.scatter(cpu_means_decimal, ram_means_decimal, c=colors, s=100, alpha=0.7)
        ax9.set_xlabel('CPU Utilization')
        ax9.set_ylabel('RAM Utilization')
        ax9.set_title('CPU vs RAM Utilization Balance', fontweight='bold', fontsize=12)
        ax9.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Perfect Balance')
        ax9.axhline(y=0.7, color='red', linestyle=':', alpha=0.5, label='Target RAM')
        ax9.axvline(x=0.7, color='red', linestyle=':', alpha=0.5, label='Target CPU')
        ax9.legend()
        
        # Add algorithm labels
        for i, alg in enumerate(algorithms):
            ax9.annotate(alg, (cpu_means_decimal[i], ram_means_decimal[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('results/comprehensive_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_radar_plot(self):
        """Create radar plot for multi-dimensional performance analysis"""
        if not self.results:
            return
        
        # Define metrics for radar plot (normalize to 0-1 scale)
        metrics = ['Energy Efficiency', 'Cost Efficiency', 'CPU Utilization', 
                  'RAM Utilization', 'SLA Compliance', 'Success Rate']
        
        # Prepare data
        radar_data = {}
        for alg in self.algorithms:
            # Normalize metrics (higher is better for all)
            energy_eff = 1 - (self.results[alg]['total_energy_consumption_mean'] / 
                             max([self.results[a]['total_energy_consumption_mean'] for a in self.algorithms]))
            cost_eff = 1 - (self.results[alg]['total_cost_mean'] / 
                           max([self.results[a]['total_cost_mean'] for a in self.algorithms]))
            cpu_util = min(self.results[alg]['average_cpu_utilization_mean'] / 0.7, 1.0)  # Normalize to 70% target
            ram_util = min(self.results[alg]['average_ram_utilization_mean'] / 0.7, 1.0)
            sla_comp = 1 - (self.results[alg]['sla_violations_mean'] / 
                           max([self.results[a]['sla_violations_mean'] for a in self.algorithms])) if max([self.results[a]['sla_violations_mean'] for a in self.algorithms]) > 0 else 1
            success_rate = self.results[alg]['placement_success_rate_mean']
            
            radar_data[alg] = [energy_eff, cost_eff, cpu_util, ram_util, sla_comp, success_rate]
        
        # Create radar plot
        fig, axes = plt.subplots(2, 2, figsize=(16, 12), subplot_kw=dict(projection='polar'))
        axes = axes.flatten()
        
        # Colors for different algorithm types
        ai_algorithms = [alg for alg in self.algorithms if 'AI' in alg or 'Hybrid' in alg]
        traditional_algorithms = [alg for alg in self.algorithms if alg not in ai_algorithms]
        
        # Plot AI algorithms
        for i, alg in enumerate(ai_algorithms[:4]):  # Up to 4 AI algorithms
            ax = axes[i]
            values = radar_data[alg]
            values += values[:1]  # Complete the circle
            
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            angles += angles[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=alg, color='red')
            ax.fill(angles, values, alpha=0.25, color='red')
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics)
            ax.set_ylim(0, 1)
            ax.set_title(f'{alg} Performance', fontweight='bold', pad=20)
            ax.grid(True)
        
        # If we have fewer than 4 AI algorithms, use remaining space for traditional
        remaining_axes = len(ai_algorithms)
        for i, alg in enumerate(['Worst-Fit', 'Best-Fit', 'Random'][:4-remaining_axes]):
            if alg in radar_data:
                ax = axes[remaining_axes + i]
                values = radar_data[alg]
                values += values[:1]
                
                angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
                angles += angles[:1]
                
                color = '#45B7D1' if alg == 'Worst-Fit' else '#96CEB4'
                ax.plot(angles, values, 'o-', linewidth=2, label=alg, color=color)
                ax.fill(angles, values, alpha=0.25, color=color)
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(metrics)
                ax.set_ylim(0, 1)
                ax.set_title(f'{alg} Performance', fontweight='bold', pad=20)
                ax.grid(True)
        
        plt.tight_layout()
        plt.savefig('results/radar_plot_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_load_balancing_analysis(self):
        """Create comprehensive load balancing visualizations"""
        if not self.results:
            return
        
        # Check if load balancing metrics are available
        has_lb_metrics = any('cpu_variance' in str(self.results[alg]) for alg in self.algorithms)
        
        if not has_lb_metrics:
            print("Load balancing metrics not available in results")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Extract load balancing metrics
        algorithms = self.algorithms
        try:
            cpu_variances = [self.results[alg].get('cpu_variance_mean', 0) for alg in algorithms]
            ram_variances = [self.results[alg].get('ram_variance_mean', 0) for alg in algorithms]
            cpu_lb_indices = [self.results[alg].get('cpu_load_balancing_index_mean', 0) for alg in algorithms]
            ram_lb_indices = [self.results[alg].get('ram_load_balancing_index_mean', 0) for alg in algorithms]
            cpu_fairness = [self.results[alg].get('cpu_fairness_index_mean', 1) for alg in algorithms]
            ram_fairness = [self.results[alg].get('ram_fairness_index_mean', 1) for alg in algorithms]
        except:
            print("Load balancing metrics format not supported")
            return
        
        # Color scheme
        colors = ['#FF6B6B' if 'AI' in alg or 'Hybrid' in alg else 
                 '#4ECDC4' if 'LB' in alg or 'Adaptive' in alg else
                 '#45B7D1' if alg == 'Worst-Fit' else '#96CEB4' for alg in algorithms]
        
        # 1. CPU Variance (lower is better)
        ax1 = axes[0, 0]
        bars1 = ax1.bar(range(len(algorithms)), cpu_variances, color=colors, alpha=0.8)
        ax1.set_title('CPU Utilization Variance\n(Lower = Better Load Balance)', fontweight='bold')
        ax1.set_ylabel('Variance')
        ax1.set_xticks(range(len(algorithms)))
        ax1.set_xticklabels(algorithms, rotation=45, ha='right')
        
        # 2. RAM Variance (lower is better)
        ax2 = axes[0, 1]
        bars2 = ax2.bar(range(len(algorithms)), ram_variances, color=colors, alpha=0.8)
        ax2.set_title('RAM Utilization Variance\n(Lower = Better Load Balance)', fontweight='bold')
        ax2.set_ylabel('Variance')
        ax2.set_xticks(range(len(algorithms)))
        ax2.set_xticklabels(algorithms, rotation=45, ha='right')
        
        # 3. Load Balancing Index
        ax3 = axes[0, 2]
        combined_lb_index = [(cpu + ram) / 2 for cpu, ram in zip(cpu_lb_indices, ram_lb_indices)]
        bars3 = ax3.bar(range(len(algorithms)), combined_lb_index, color=colors, alpha=0.8)
        ax3.set_title('Combined Load Balancing Index\n(Lower = Better)', fontweight='bold')
        ax3.set_ylabel('LB Index')
        ax3.set_xticks(range(len(algorithms)))
        ax3.set_xticklabels(algorithms, rotation=45, ha='right')
        
        # 4. Fairness Index (higher is better)
        ax4 = axes[1, 0]
        combined_fairness = [(cpu + ram) / 2 for cpu, ram in zip(cpu_fairness, ram_fairness)]
        bars4 = ax4.bar(range(len(algorithms)), combined_fairness, color=colors, alpha=0.8)
        ax4.set_title('Fairness Index\n(Higher = More Fair)', fontweight='bold')
        ax4.set_ylabel('Fairness (0-1)')
        ax4.set_xticks(range(len(algorithms)))
        ax4.set_xticklabels(algorithms, rotation=45, ha='right')
        ax4.axhline(y=0.8, color='red', linestyle='--', alpha=0.7, label='Good Fairness')
        ax4.legend()
        
        # 5. Load Balance vs Performance Trade-off
        ax5 = axes[1, 1]
        efficiency_scores = []
        for alg in algorithms:
            energy_means = [self.results[a]['total_energy_consumption_mean'] for a in algorithms]
            cost_means = [self.results[a]['total_cost_mean'] for a in algorithms]
            
            energy_norm = 1 - (self.results[alg]['total_energy_consumption_mean'] / max(energy_means))
            cost_norm = 1 - (self.results[alg]['total_cost_mean'] / max(cost_means))
            efficiency = (energy_norm + cost_norm) / 2
            efficiency_scores.append(efficiency)
        
        scatter5 = ax5.scatter(combined_lb_index, efficiency_scores, c=colors, s=100, alpha=0.7)
        ax5.set_xlabel('Load Balance Index (Lower = Better)')
        ax5.set_ylabel('Performance Efficiency (Higher = Better)')
        ax5.set_title('Load Balance vs Performance Trade-off', fontweight='bold')
        
        # Add algorithm labels
        for i, alg in enumerate(algorithms):
            ax5.annotate(alg, (combined_lb_index[i], efficiency_scores[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # 6. Resource Utilization Distribution
        ax6 = axes[1, 2]
        cpu_means = [self.results[alg]['average_cpu_utilization_mean'] * 100 for alg in algorithms]
        ram_means = [self.results[alg]['average_ram_utilization_mean'] * 100 for alg in algorithms]
        
        x = np.arange(len(algorithms))
        width = 0.35
        
        bars6_cpu = ax6.bar(x - width/2, cpu_means, width, label='CPU', alpha=0.8, color='skyblue')
        bars6_ram = ax6.bar(x + width/2, ram_means, width, label='RAM', alpha=0.8, color='lightcoral')
        
        ax6.set_title('Resource Utilization Distribution', fontweight='bold')
        ax6.set_ylabel('Utilization (%)')
        ax6.set_xticks(x)
        ax6.set_xticklabels(algorithms, rotation=45, ha='right')
        ax6.legend()
        ax6.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Target')
        
        plt.tight_layout()
        plt.savefig('results/load_balancing_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_performance_heatmap(self):
        """Create performance heatmap for easy comparison"""
        if not self.results:
            return
        
        # Prepare data for heatmap
        metrics = ['Energy', 'Cost', 'CPU Util', 'RAM Util', 'SLA Violations', 'Success Rate']
        data = []
        
        for alg in self.algorithms:
            # Normalize all metrics to 0-100 scale (higher is better)
            energy_means = [self.results[a]['total_energy_consumption_mean'] for a in self.algorithms]
            cost_means = [self.results[a]['total_cost_mean'] for a in self.algorithms]
            sla_means = [self.results[a]['sla_violations_mean'] for a in self.algorithms]
            
            energy_score = (1 - (self.results[alg]['total_energy_consumption_mean'] / max(energy_means))) * 100
            cost_score = (1 - (self.results[alg]['total_cost_mean'] / max(cost_means))) * 100
            cpu_score = min(self.results[alg]['average_cpu_utilization_mean'] / 0.7 * 100, 100)
            ram_score = min(self.results[alg]['average_ram_utilization_mean'] / 0.7 * 100, 100)
            sla_score = (1 - (self.results[alg]['sla_violations_mean'] / max(sla_means))) * 100 if max(sla_means) > 0 else 100
            success_score = self.results[alg]['placement_success_rate_mean'] * 100
            
            data.append([energy_score, cost_score, cpu_score, ram_score, sla_score, success_score])
        
        # Create heatmap
        plt.figure(figsize=(12, 8))
        
        # Create DataFrame for easier handling
        df = pd.DataFrame(data, index=self.algorithms, columns=metrics)
        
        # Create heatmap with custom colormap
        sns.heatmap(df, annot=True, fmt='.1f', cmap='RdYlGn', center=50,
                   cbar_kws={'label': 'Performance Score (0-100)'})
        
        plt.title('Algorithm Performance Heatmap\n(Higher Values = Better Performance)', 
                 fontweight='bold', fontsize=14)
        plt.xlabel('Performance Metrics', fontweight='bold')
        plt.ylabel('Algorithms', fontweight='bold')
        
        # Rotate y-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        plt.tight_layout()
        plt.savefig('results/performance_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def create_statistical_analysis(self):
        """Create statistical analysis plots with confidence intervals"""
        if not self.results:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Energy consumption with confidence intervals
        ax1 = axes[0, 0]
        energy_means = [self.results[alg]['total_energy_consumption_mean'] for alg in self.algorithms]
        energy_stds = [self.results[alg]['total_energy_consumption_std'] for alg in self.algorithms]
        
        # Calculate 95% confidence intervals (assuming normal distribution)
        confidence_intervals = [1.96 * std / np.sqrt(5) for std in energy_stds]  # 5 runs
        
        colors = ['#FF6B6B' if 'AI' in alg else '#96CEB4' for alg in self.algorithms]
        bars1 = ax1.bar(range(len(self.algorithms)), energy_means, yerr=confidence_intervals,
                       color=colors, alpha=0.8, capsize=5)
        ax1.set_title('Energy Consumption (95% CI)', fontweight='bold')
        ax1.set_ylabel('Watts')
        ax1.set_xticks(range(len(self.algorithms)))
        ax1.set_xticklabels(self.algorithms, rotation=45, ha='right')
        
        # 2. Cost with confidence intervals
        ax2 = axes[0, 1]
        cost_means = [self.results[alg]['total_cost_mean'] for alg in self.algorithms]
        cost_stds = [self.results[alg]['total_cost_std'] for alg in self.algorithms]
        cost_ci = [1.96 * std / np.sqrt(5) for std in cost_stds]
        
        bars2 = ax2.bar(range(len(self.algorithms)), cost_means, yerr=cost_ci,
                       color=colors, alpha=0.8, capsize=5)
        ax2.set_title('Total Cost (95% CI)', fontweight='bold')
        ax2.set_ylabel('Dollars')
        ax2.set_xticks(range(len(self.algorithms)))
        ax2.set_xticklabels(self.algorithms, rotation=45, ha='right')
        
        # 3. Box plot for energy distribution
        ax3 = axes[1, 0]
        energy_values = []
        labels = []
        for alg in self.algorithms:
            if f'{alg}_values' in str(self.results[alg]):
                values = self.results[alg]['total_energy_consumption_values']
                energy_values.append(values)
                labels.append(alg)
        
        if energy_values:
            box_plot = ax3.boxplot(energy_values, labels=labels, patch_artist=True)
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
        
        ax3.set_title('Energy Consumption Distribution', fontweight='bold')
        ax3.set_ylabel('Watts')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Performance consistency (coefficient of variation)
        ax4 = axes[1, 1]
        cv_data = []
        cv_labels = []
        
        for alg in self.algorithms:
            # Calculate coefficient of variation for different metrics
            energy_cv = self.results[alg]['total_energy_consumption_std'] / self.results[alg]['total_energy_consumption_mean']
            cost_cv = self.results[alg]['total_cost_std'] / self.results[alg]['total_cost_mean']
            avg_cv = (energy_cv + cost_cv) / 2
            cv_data.append(avg_cv)
            cv_labels.append(alg)
        
        bars4 = ax4.bar(range(len(cv_labels)), cv_data, color=colors, alpha=0.8)
        ax4.set_title('Performance Consistency\n(Lower = More Consistent)', fontweight='bold')
        ax4.set_ylabel('Coefficient of Variation')
        ax4.set_xticks(range(len(cv_labels)))
        ax4.set_xticklabels(cv_labels, rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig('results/statistical_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_all_visualizations(self):
        """Generate all visualization types"""
        print("Generating comprehensive visualization suite...")
        
        print("1. Creating comprehensive comparison charts...")
        self.create_comprehensive_comparison()
        
        print("2. Creating radar plots...")
        self.create_radar_plot()
        
        print("3. Creating load balancing analysis...")
        self.create_load_balancing_analysis()
        
        print("4. Creating performance heatmap...")
        self.create_performance_heatmap()
        
        print("5. Creating statistical analysis...")
        self.create_statistical_analysis()
        
        print("All visualizations generated and saved to results/ folder!")

def main():
    """Main function to generate all visualizations"""
    viz = AdvancedVisualizationSuite()
    viz.generate_all_visualizations()

if __name__ == "__main__":
    main()