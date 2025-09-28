#!/usr/bin/env python3
"""
Enhanced VM Placement Simulation System - Web Application
A comprehensive web interface for enterprise VM placement management
"""

import os
import sys
import json
import datetime
import random
from typing import Dict, List, Any, Optional
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import logging

# Set up matplotlib style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Configure Flask app
app = Flask(__name__)
app.secret_key = 'vm_placement_secret_key_2024'
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data classes for demonstration
class TenantType:
    STANDARD = "standard"
    ENHANCED = "enhanced" 
    DEDICATED = "dedicated"
    GOVERNMENT = "government"

class TenantProfile:
    def __init__(self, tenant_id: str, name: str, tenant_type: str, compliance: List[str], **kwargs):
        self.tenant_id = tenant_id
        self.name = name
        self.type = tenant_type
        self.compliance = compliance
        self.__dict__.update(kwargs)

class VMRequest:
    def __init__(self, vm_id: str, tenant_id: str, cpu_required: int, ram_required: int, 
                 storage_required: int = 100, workload_type: str = "web"):
        self.vm_id = vm_id
        self.tenant_id = tenant_id
        self.cpu_required = cpu_required
        self.ram_required = ram_required
        self.storage_required = storage_required
        self.workload_type = workload_type

class PlacementResult:
    def __init__(self, success: bool, host_id: str = None, message: str = ""):
        self.success = success
        self.host_id = host_id
        self.message = message

class PlacementRecord:
    def __init__(self, vm_request: VMRequest, result: PlacementResult, timestamp: str):
        self.vm_request = vm_request
        self.result = result
        self.timestamp = timestamp

def create_sample_tenants():
    """Create sample tenant data"""
    return {
        "healthcare_corp": TenantProfile(
            tenant_id="healthcare_corp",
            name="Healthcare Corp",
            tenant_type=TenantType.ENHANCED,
            compliance=["HIPAA", "SOC2"],
            budget_limit=50000,
            current_usage=32000,
            priority="high"
        ),
        "fintech_startup": TenantProfile(
            tenant_id="fintech_startup", 
            name="FinTech Startup",
            tenant_type=TenantType.STANDARD,
            compliance=["PCI-DSS"],
            budget_limit=25000,
            current_usage=18000,
            priority="medium"
        ),
        "government_agency": TenantProfile(
            tenant_id="government_agency",
            name="Government Agency",
            tenant_type=TenantType.GOVERNMENT,
            compliance=["FedRAMP", "FISMA"],
            budget_limit=100000,
            current_usage=45000,
            priority="high"
        ),
        "ecommerce_platform": TenantProfile(
            tenant_id="ecommerce_platform",
            name="E-commerce Platform",
            tenant_type=TenantType.STANDARD,
            compliance=["SOC2"],
            budget_limit=40000,
            current_usage=35000,
            priority="medium"
        )
    }

def create_sample_data():
    """Create sample data for demonstration"""
    sample_tenants = create_sample_tenants()
    
    # Sample placement history
    placement_history = []
    tenant_ids = list(sample_tenants.keys())
    workload_types = ['web', 'database', 'ml_training', 'batch_processing']
    
    for i in range(50):
        vm_request = VMRequest(
            vm_id=f'vm_{i+1:03d}',
            tenant_id=random.choice(tenant_ids),
            cpu_required=random.choice([2, 4, 8, 16]),
            ram_required=random.choice([4, 8, 16, 32]),
            storage_required=random.choice([100, 250, 500, 1000]),
            workload_type=random.choice(workload_types)
        )
        
        result = PlacementResult(
            success=random.random() > 0.05,  # 95% success rate
            host_id=f'host_{random.randint(1, 20):02d}' if random.random() > 0.05 else None,
            message="Placement successful" if random.random() > 0.05 else "No suitable host found"
        )
        
        timestamp = datetime.datetime.now() - datetime.timedelta(
            hours=random.randint(0, 72),
            minutes=random.randint(0, 59)
        )
        
        placement_history.append(PlacementRecord(
            vm_request=vm_request,
            result=result,
            timestamp=timestamp.isoformat()
        ))
    
    # Sort by timestamp
    placement_history.sort(key=lambda x: x.timestamp, reverse=True)
    
    return sample_tenants, placement_history

def get_host_data():
    """Generate detailed host data for demonstration"""
    host_types = [
        {"cpu_cores": 16, "ram_gb": 64, "base_power_watts": 200, "cost_per_hour": 0.8},
        {"cpu_cores": 32, "ram_gb": 128, "base_power_watts": 350, "cost_per_hour": 1.5},
        {"cpu_cores": 64, "ram_gb": 256, "base_power_watts": 500, "cost_per_hour": 2.2},
        {"cpu_cores": 8, "ram_gb": 32, "base_power_watts": 120, "cost_per_hour": 0.5},
    ]
    
    hosts = []
    for i in range(20):
        base_type = random.choice(host_types)
        variation = 0.9 + np.random.random() * 0.2
        
        host = {
            "host_id": f"host_{i+1:02d}",
            "cpu_cores": int(base_type["cpu_cores"] * variation),
            "ram_gb": int(base_type["ram_gb"] * variation),
            "base_power_watts": base_type["base_power_watts"] * variation,
            "cost_per_hour": base_type["cost_per_hour"] * variation,
            "sla_risk_factor": np.random.uniform(0.01, 0.05),
            "status": "active" if random.random() > 0.1 else "maintenance"
        }
        
        # Simulate utilization
        host["current_cpu_usage"] = random.uniform(0.1, 0.9) * host["cpu_cores"]
        host["current_ram_usage"] = random.uniform(0.1, 0.9) * host["ram_gb"]
        
        # Calculate derived metrics
        cpu_util = host["current_cpu_usage"] / host["cpu_cores"]
        ram_util = host["current_ram_usage"] / host["ram_gb"]
        power_multiplier = 0.3 + 0.7 * (cpu_util ** 1.3)
        host["current_power_watts"] = host["base_power_watts"] * power_multiplier
        
        hosts.append(host)
        
    return hosts

def generate_plot_base64(fig):
    """Convert matplotlib figure to base64 string"""
    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    plot_data = buffer.getvalue()
    buffer.close()
    plt.close(fig)
    return base64.b64encode(plot_data).decode()

def calculate_system_stats(placement_history):
    """Calculate system statistics"""
    successful_placements = sum(1 for p in placement_history if p.result.success)
    total_placements = len(placement_history)
    
    # Calculate resource allocation
    total_cpu = sum(p.vm_request.cpu_required for p in placement_history if p.result.success)
    total_ram = sum(p.vm_request.ram_required for p in placement_history if p.result.success)
    
    return {
        'total_placements': total_placements,
        'success_rate': (successful_placements / total_placements * 100) if total_placements > 0 else 0,
        'avg_compliance_score': 0.995,  # High compliance score
        'active_tenants': len(create_sample_tenants()),
        'total_resources_allocated': {
            'cpu': total_cpu,
            'ram': total_ram
        }
    }

@app.route('/')
def dashboard():
    """Main dashboard view"""
    try:
        sample_tenants, placement_history = create_sample_data()
        recent_placements = placement_history[:15]
        system_stats = calculate_system_stats(placement_history)
        
        # Create tenant summaries
        tenant_summaries = {}
        for tenant_id, tenant in sample_tenants.items():
            tenant_placements = [p for p in placement_history if p.vm_request.tenant_id == tenant_id and p.result.success]
            
            total_cpu = sum(p.vm_request.cpu_required for p in tenant_placements)
            total_ram = sum(p.vm_request.ram_required for p in tenant_placements)
            vm_count = len(tenant_placements)
            
            # Calculate cost status
            usage_ratio = tenant.current_usage / tenant.budget_limit
            if usage_ratio < 0.7:
                cost_status = 'within_budget'
            elif usage_ratio < 0.9:
                cost_status = 'approaching_limit'
            else:
                cost_status = 'over_budget'
            
            tenant_summaries[tenant_id] = {
                'tenant_name': tenant.name,
                'usage_summary': {
                    'vm_count': vm_count,
                    'total_cpu': total_cpu,
                    'total_ram': total_ram
                },
                'cost_status': cost_status
            }
        
        return render_template('dashboard.html', 
                             recent_placements=recent_placements,
                             system_stats=system_stats,
                             tenant_summaries=tenant_summaries,
                             active_hosts=18,
                             total_hosts=20)
    
    except Exception as e:
        logger.error(f"Error in dashboard route: {e}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('error.html', error=str(e))

@app.route('/placement')
def placement_interface():
    """VM Placement interface"""
    try:
        sample_tenants, _ = create_sample_data()
        
        workload_types = [
            {'id': 'web', 'name': 'Web Server', 'description': 'Standard web application hosting'},
            {'id': 'database', 'name': 'Database', 'description': 'Database server with high I/O requirements'},
            {'id': 'ml_training', 'name': 'ML Training', 'description': 'Machine learning model training workload'},
            {'id': 'batch_processing', 'name': 'Batch Processing', 'description': 'Large-scale data processing'}
        ]
        
        return render_template('placement.html', 
                             tenants=sample_tenants, 
                             workload_types=workload_types)
    
    except Exception as e:
        logger.error(f"Error in placement route: {e}")
        flash(f'Error loading placement interface: {str(e)}', 'error')
        return render_template('error.html', error=str(e))

@app.route('/api/placement', methods=['POST'])
def api_placement():
    """API endpoint for VM placement requests"""
    try:
        data = request.json
        
        # Simulate placement logic
        success = random.random() > 0.1  # 90% success rate
        
        result = {
            'success': success,
            'placement_id': f'placement_{datetime.datetime.now().timestamp()}',
            'execution_time_ms': round(random.uniform(5, 50), 2),
            'cost_efficiency': round(random.uniform(0.85, 0.99), 3),
            'energy_efficiency': round(random.uniform(0.80, 0.95), 3),
            'compliance_score': 1.0
        }
        
        if success:
            result.update({
                'assigned_host': f'host_{random.randint(1, 20):02d}',
                'optimizations': [
                    'Energy consumption optimized',
                    'Cost efficiency maximized', 
                    'SLA requirements satisfied',
                    'Compliance constraints met'
                ]
            })
        else:
            result.update({
                'error': 'No suitable host found for placement',
                'suggestions': [
                    'Reduce resource requirements',
                    'Try different workload type',
                    'Check tenant constraints'
                ]
            })
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in placement API: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/tenants')
def tenants_view():
    """Tenant management view"""
    try:
        sample_tenants, placement_history = create_sample_data()
        
        tenant_stats = {}
        for tenant_id, tenant in sample_tenants.items():
            tenant_placements = [p for p in placement_history if p.vm_request.tenant_id == tenant_id]
            successful_placements = [p for p in tenant_placements if p.result.success]
            
            tenant_stats[tenant_id] = {
                'total_placements': len(tenant_placements),
                'success_rate': (len(successful_placements) / len(tenant_placements) * 100) if tenant_placements else 0,
                'avg_cost_efficiency': random.uniform(85, 95),
                'compliance_score': 100.0
            }
        
        return render_template('tenants.html', 
                             tenants=sample_tenants, 
                             tenant_stats=tenant_stats)
    
    except Exception as e:
        logger.error(f"Error in tenants route: {e}")
        flash(f'Error loading tenant information: {str(e)}', 'error')
        return render_template('error.html', error=str(e))

@app.route('/audit')
def audit_view():
    """Audit and compliance view"""
    try:
        _, placement_history = create_sample_data()
        
        audit_data = {
            'total_placements': len(placement_history),
            'compliance_violations': 0,
            'security_incidents': 0,
            'avg_response_time': random.uniform(10, 30),
            'recent_activities': placement_history[:20]
        }
        
        # Create audit visualization
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Audit & Compliance Dashboard', fontsize=16, fontweight='bold')
        
        # Mock time series data
        timestamps = [datetime.datetime.now() - datetime.timedelta(hours=i) for i in range(24, 0, -1)]
        
        # Compliance score over time (always 100%)
        compliance_scores = [100] * len(timestamps)
        ax1.plot(timestamps, compliance_scores, 'g-', linewidth=3, marker='o', markersize=4)
        ax1.set_title('Compliance Score Over Time')
        ax1.set_ylabel('Compliance Score (%)')
        ax1.set_ylim(95, 105)
        ax1.grid(True, alpha=0.3)
        
        # Response time trend
        response_times = [random.uniform(10, 40) for _ in timestamps]
        ax2.plot(timestamps, response_times, 'b-', linewidth=2, marker='s', markersize=4)
        ax2.set_title('Response Time Trend')
        ax2.set_ylabel('Response Time (ms)')
        ax2.grid(True, alpha=0.3)
        
        # Workload distribution
        workload_counts = {'web': 20, 'database': 15, 'ml_training': 8, 'batch_processing': 7}
        ax3.bar(workload_counts.keys(), workload_counts.values(), 
                color=['lightblue', 'lightgreen', 'lightyellow', 'lightcoral'], 
                edgecolor='black')
        ax3.set_title('Workload Distribution')
        ax3.set_ylabel('Count')
        ax3.tick_params(axis='x', rotation=45)
        
        # Success vs failure
        success_count = sum(1 for p in placement_history if p.result.success)
        failure_count = len(placement_history) - success_count
        ax4.pie([success_count, failure_count], 
                labels=['Success', 'Failure'], 
                colors=['green', 'red'], 
                autopct='%1.1f%%',
                startangle=90)
        ax4.set_title('Placement Success Rate')
        
        plt.tight_layout()
        audit_plot = generate_plot_base64(fig)
        
        audit_data['audit_plot'] = audit_plot
        
        return render_template('audit.html', **audit_data)
    
    except Exception as e:
        logger.error(f"Error in audit route: {e}")
        flash(f'Error loading audit information: {str(e)}', 'error')
        return render_template('error.html', error=str(e))

@app.route('/analytics')
def analytics_view():
    """Reports and analytics view"""
    try:
        sample_tenants, placement_history = create_sample_data()
        
        # Calculate performance metrics
        successful_placements = [p for p in placement_history if p.result.success]
        success_rate = len(successful_placements) / len(placement_history) * 100
        
        reports_data = {
            'performance_summary': {
                'total_placements': len(placement_history),
                'success_rate': success_rate,
                'avg_response_time': random.uniform(15, 25),
                'avg_cost_efficiency': random.uniform(88, 95),
                'avg_energy_efficiency': random.uniform(82, 92)
            }
        }
        
        # Create comprehensive analytics chart
        fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(16, 10))
        fig.suptitle('Comprehensive Analytics Report', fontsize=16, fontweight='bold')
        
        # Generate time series data
        hours = list(range(24, 0, -1))
        timestamps = [datetime.datetime.now() - datetime.timedelta(hours=h) for h in hours]
        
        # 1. Success rate trend
        success_values = [random.uniform(90, 100) for _ in hours]
        ax1.plot(timestamps, success_values, 'g-', linewidth=2, marker='o', markersize=3)
        ax1.set_title('Success Rate Trend')
        ax1.set_ylabel('Success Rate (%)')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(85, 105)
        
        # 2. Cost efficiency trend  
        cost_eff = [random.uniform(85, 95) for _ in hours]
        ax2.plot(timestamps, cost_eff, 'b-', linewidth=2, marker='s', markersize=3)
        ax2.set_title('Cost Efficiency Trend')
        ax2.set_ylabel('Cost Efficiency (%)')
        ax2.grid(True, alpha=0.3)
        
        # 3. Energy efficiency trend
        energy_eff = [random.uniform(80, 92) for _ in hours]
        ax3.plot(timestamps, energy_eff, 'orange', linewidth=2, marker='^', markersize=3)
        ax3.set_title('Energy Efficiency Trend')
        ax3.set_ylabel('Energy Efficiency (%)')
        ax3.grid(True, alpha=0.3)
        
        # 4. Response time distribution
        response_times = [random.uniform(5, 50) for _ in range(50)]
        ax4.hist(response_times, bins=10, color='lightgreen', alpha=0.7, edgecolor='black')
        ax4.set_title('Response Time Distribution')
        ax4.set_xlabel('Response Time (ms)')
        ax4.set_ylabel('Frequency')
        
        # 5. Tenant activity
        tenant_counts = {}
        for p in placement_history:
            tenant_id = p.vm_request.tenant_id
            tenant_counts[tenant_id] = tenant_counts.get(tenant_id, 0) + 1
        
        ax5.bar(range(len(tenant_counts)), list(tenant_counts.values()), 
                color='lightcoral', edgecolor='black')
        ax5.set_title('Tenant Activity')
        ax5.set_xlabel('Tenant')
        ax5.set_ylabel('Placements')
        ax5.set_xticks(range(len(tenant_counts)))
        ax5.set_xticklabels([t[:8] + '...' for t in tenant_counts.keys()], rotation=45)
        
        # 6. Efficiency correlation
        cost_vals = [random.uniform(85, 95) for _ in range(30)]
        energy_vals = [random.uniform(80, 92) for _ in range(30)]
        ax6.scatter(cost_vals, energy_vals, alpha=0.6, s=50, c='purple')
        ax6.set_title('Cost vs Energy Efficiency')
        ax6.set_xlabel('Cost Efficiency (%)')
        ax6.set_ylabel('Energy Efficiency (%)')
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        reports_plot = generate_plot_base64(fig)
        
        reports_data['reports_plot'] = reports_plot
        
        return render_template('reports.html', **reports_data)
    
    except Exception as e:
        logger.error(f"Error in reports route: {e}")
        flash(f'Error loading reports: {str(e)}', 'error')
        return render_template('error.html', error=str(e))

@app.route('/api/system_status')
def api_system_status():
    """API endpoint for system status"""
    try:
        _, placement_history = create_sample_data()
        system_stats = calculate_system_stats(placement_history)
        
        # Generate host utilization data
        host_utilizations = []
        for i in range(1, 21):  # 20 hosts
            host_utilizations.append({
                'host_id': f'{i:02d}',
                'cpu_utilization': random.uniform(20, 85),
                'ram_utilization': random.uniform(30, 90),
                'status': 'active' if random.random() > 0.1 else 'maintenance'
            })
        
        return jsonify({
            'system_stats': system_stats,
            'host_utilizations': host_utilizations,
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in system status API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/hosts')
def hosts_view():
    """Host management view"""
    try:
        hosts = get_host_data()
        
        # Create visualizations
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # CPU vs RAM Utilization
        cpu_utils = [(h['current_cpu_usage'] / h['cpu_cores']) * 100 for h in hosts]
        ram_utils = [(h['current_ram_usage'] / h['ram_gb']) * 100 for h in hosts]
        host_ids = [h['host_id'] for h in hosts]
        
        ax1.bar(host_ids, cpu_utils, label='CPU')
        ax1.bar(host_ids, ram_utils, bottom=cpu_utils, label='RAM')
        ax1.set_title('CPU and RAM Utilization per Host')
        ax1.set_ylabel('Utilization (%)')
        ax1.set_xticklabels(host_ids, rotation=90)
        ax1.legend()
        
        # Power vs Utilization
        power_watts = [h['current_power_watts'] for h in hosts]
        avg_utils = [(cpu + ram) / 2 for cpu, ram in zip(cpu_utils, ram_utils)]
        
        ax2.scatter(avg_utils, power_watts)
        ax2.set_title('Power Consumption vs. Utilization')
        ax2.set_xlabel('Average Utilization (%)')
        ax2.set_ylabel('Power (Watts)')
        
        plt.tight_layout()
        charts = generate_plot_base64(fig)
        
        return render_template('hosts.html', hosts=hosts, charts=charts)
    
    except Exception as e:
        logger.error(f"Error in hosts route: {e}")
        flash(f'Error loading host information: {str(e)}', 'error')
        return render_template('error.html', error=str(e))

@app.route('/comparison')
def comparison_view():
    """Comparison report view"""
    try:
        data = [
            {'Algorithm': 'Hybrid-AI', 'total_energy_consumption_mean': 32504.8532625, 'total_energy_consumption_std': 15.0, 'total_cost_mean': 5771.98509375, 'total_cost_std': 5.0, 'average_cpu_utilization_mean': 0.95, 'average_cpu_utilization_std': 0.05, 'average_ram_utilization_mean': 0.7760942425, 'average_ram_utilization_std': 0.05, 'sla_violations_mean': 54, 'sla_violations_std': 1, 'placement_success_rate_mean': 0.2548, 'placement_success_rate_std': 0.0, 'cpu_variance': 0.05, 'ram_variance': 0.06, 'jains_fairness': 0.924, 'performance_score': 0.9},
            {'Algorithm': 'AI-Predictor', 'total_energy_consumption_mean': 59055.29691, 'total_energy_consumption_std': 3805.956602, 'total_cost_mean': 9341.460346, 'total_cost_std': 1029.767748, 'average_cpu_utilization_mean': 0.905196325, 'average_cpu_utilization_std': 0.020104864, 'average_ram_utilization_mean': 0.581778098, 'average_ram_utilization_std': 0.007289243, 'sla_violations_mean': 88.6, 'sla_violations_std': 6.343500611, 'placement_success_rate_mean': 0.1806, 'placement_success_rate_std': 0.00989141, 'cpu_variance': 0.25, 'ram_variance': 0.28, 'jains_fairness': 0.65, 'performance_score': 0.13},
            {'Algorithm': 'Best-Fit', 'total_energy_consumption_mean': 56326.70871, 'total_energy_consumption_std': 5172.946081, 'total_cost_mean': 9009.14705, 'total_cost_std': 1172.347121, 'average_cpu_utilization_mean': 0.8707452, 'average_cpu_utilization_std': 0.040248042, 'average_ram_utilization_mean': 0.586805563, 'average_ram_utilization_std': 0.029732259, 'sla_violations_mean': 81.2, 'sla_violations_std': 11.72006826, 'placement_success_rate_mean': 0.1796, 'placement_success_rate_std': 0.009541488, 'cpu_variance': 0.30, 'ram_variance': 0.32, 'jains_fairness': 0.60, 'performance_score': 0.13},
            {'Algorithm': 'First-Fit', 'total_energy_consumption_mean': 57900.1013, 'total_energy_consumption_std': 5700.620118, 'total_cost_mean': 9137.882761, 'total_cost_std': 1238.289093, 'average_cpu_utilization_mean': 0.903211864, 'average_cpu_utilization_std': 0.030320678, 'average_ram_utilization_mean': 0.61486694, 'average_ram_utilization_std': 0.007196248, 'sla_violations_mean': 92.6, 'sla_violations_std': 7.059745038, 'placement_success_rate_mean': 0.1816, 'placement_success_rate_std': 0.010892199, 'cpu_variance': 0.28, 'ram_variance': 0.29, 'jains_fairness': 0.62, 'performance_score': 0.14},
            {'Algorithm': 'Worst-Fit', 'total_energy_consumption_mean': 43339.80435, 'total_energy_consumption_std': 2370.096841, 'total_cost_mean': 7695.980125, 'total_cost_std': 740.1739555, 'average_cpu_utilization_mean': 0.732392402, 'average_cpu_utilization_std': 0.017232869, 'average_ram_utilization_mean': 0.620875394, 'average_ram_utilization_std': 0.015769527, 'sla_violations_mean': 76, 'sla_violations_std': 4.604345773, 'placement_success_rate_mean': 0.196, 'placement_success_rate_std': 0.0085557, 'cpu_variance': 0.10, 'ram_variance': 0.12, 'jains_fairness': 0.88, 'performance_score': 0.13},
            {'Algorithm': 'Random', 'total_energy_consumption_mean': 47784.9158, 'total_energy_consumption_std': 3874.209643, 'total_cost_mean': 8060.831958, 'total_cost_std': 705.8969737, 'average_cpu_utilization_mean': 0.778251636, 'average_cpu_utilization_std': 0.013378972, 'average_ram_utilization_mean': 0.578501962, 'average_ram_utilization_std': 0.009064966, 'sla_violations_mean': 72.8, 'sla_violations_std': 5.455272679, 'placement_success_rate_mean': 0.1784, 'placement_success_rate_std': 0.011217843, 'cpu_variance': 0.15, 'ram_variance': 0.18, 'jains_fairness': 0.80, 'performance_score': 0.12},
            {'Algorithm': 'Round-Robin', 'total_energy_consumption_mean': 49882.7545, 'total_energy_consumption_std': 2591.360555, 'total_cost_mean': 8327.617273, 'total_cost_std': 920.1350405, 'average_cpu_utilization_mean': 0.809461522, 'average_cpu_utilization_std': 0.016804035, 'average_ram_utilization_mean': 0.577870371, 'average_ram_utilization_std': 0.010226879, 'sla_violations_mean': 73.2, 'sla_violations_std': 6.493073232, 'placement_success_rate_mean': 0.1812, 'placement_success_rate_std': 0.008376157, 'cpu_variance': 0.18, 'ram_variance': 0.20, 'jains_fairness': 0.75, 'performance_score': 0.13},
        ]

        charts = {}
        metrics_to_plot = {
            'placement_success_rate_mean': 'Placement Success Rate',
            'total_energy_consumption_mean': 'Total Energy Consumption',
            'total_cost_mean': 'Total Cost',
            'average_cpu_utilization_mean': 'Average CPU Utilization',
            'average_ram_utilization_mean': 'Average RAM Utilization',
            'sla_violations_mean': 'SLA Violations',
            'jains_fairness': "Jain's Fairness Index",
        }

        for metric, title in metrics_to_plot.items():
            fig, ax = plt.subplots(figsize=(10, 6))
            algorithms = [d['Algorithm'] for d in data]
            values = [d[metric] for d in data]
            
            colors = ['#FF6B6B' if alg == 'Hybrid-AI' else '#4ECDC4' for alg in algorithms]
            
            bars = ax.bar(algorithms, values, color=colors)
            ax.set_ylabel(title)
            ax.set_title(f'{title} per Algorithm')
            plt.xticks(rotation=45, ha="right")
            
            plt.tight_layout()
            charts[metric] = generate_plot_base64(fig)

        # Cost vs Efficiency Frontier
        fig, ax = plt.subplots(figsize=(10, 7))
        costs = [d['total_cost_mean'] for d in data]
        perf_scores = [d['performance_score'] for d in data]
        algorithms = [d['Algorithm'] for d in data]
        colors = ['#FF6B6B' if alg == 'Hybrid-AI' else '#4ECDC4' for alg in algorithms]
        ax.scatter(costs, perf_scores, s=150, c=colors, alpha=0.7)
        ax.set_xlabel('Total Cost ($)')
        ax.set_ylabel('Performance Score')
        ax.set_title('Cost vs. Efficiency Frontier')
        for i, txt in enumerate(algorithms):
            ax.annotate(txt, (costs[i], perf_scores[i]), xytext=(5,5), textcoords='offset points')
        plt.tight_layout()
        charts['efficiency_frontier'] = generate_plot_base64(fig)

        # Normalize data for radar chart
        metrics_for_radar = {
            'Cost': 'total_cost_mean',
            'Energy': 'total_energy_consumption_mean',
            'SLA Violations': 'sla_violations_mean',
            'CPU Utilization': 'average_cpu_utilization_mean',
            'Fairness': 'jains_fairness',
            'Success Rate': 'placement_success_rate_mean'
        }
        normalized_data = {d['Algorithm']: {} for d in data}
        for name, key in metrics_for_radar.items():
            values = [d[key] for d in data]
            min_val, max_val = min(values), max(values)
            for d in data:
                val = d[key]
                if name in ['Cost', 'Energy', 'SLA Violations']:
                    # Lower is better
                    normalized_data[d['Algorithm']][name] = (max_val - val) / (max_val - min_val) if (max_val - min_val) != 0 else 0
                else:
                    # Higher is better
                    normalized_data[d['Algorithm']][name] = (val - min_val) / (max_val - min_val) if (max_val - min_val) != 0 else 0

        # Generate radar charts
        radar_charts = {}
        labels = list(metrics_for_radar.keys())
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]

        for d in data:
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            stats = [normalized_data[d['Algorithm']][label] for label in labels]
            stats += stats[:1]
            ax.plot(angles, stats, linewidth=2, linestyle='solid')
            ax.fill(angles, stats, alpha=0.25)
            ax.set_yticklabels([])
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels)
            ax.set_title(d['Algorithm'], size=20, color='black', y=1.1)
            radar_charts[d['Algorithm']] = generate_plot_base64(fig)

        charts['radar'] = radar_charts

        return render_template('comparison.html', data=data, charts=charts)

    except Exception as e:
        logger.error(f"Error in comparison route: {e}")
        flash(f'Error loading comparison page: {str(e)}', 'error')
        return render_template('error.html', error=str(e))

@app.route('/demo')
def demo_view():
    """Interactive demo page"""
    return render_template('demo.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    try:
        # Create templates directory if it doesn't exist
        templates_dir = 'templates'
        static_dir = 'static'
        
        for directory in [templates_dir, static_dir, f'{static_dir}/css', f'{static_dir}/js']:
            os.makedirs(directory, exist_ok=True)
        
        print("🚀 Enhanced VM Placement Web Application")
        print("=" * 50)
        print("Starting web server...")
        print("Access the application at: http://localhost:5000")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        print(f"Error: {e}")
        sys.exit(1)
