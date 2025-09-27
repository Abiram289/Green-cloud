#!/usr/bin/env python3
"""
Enterprise VM Placement Web Application
Modern web frontend for the enterprise multi-tenant VM placement system
"""

import sys
import os
sys.path.append('src')

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import uuid
from typing import Dict, List

# Import our backend systems
from src.multi_tenant_placement import MultiTenantVMPlacement, TenantPolicy, DataClassification, ComplianceFramework
from src.improved_ai_algorithm import ImprovedAIPlacement
from src.data_generator import DataGenerator
from src.placement_algorithms import BestFitPlacement, FirstFitPlacement, WorstFitPlacement, RoundRobinPlacement

app = Flask(__name__)
app.secret_key = 'enterprise_vm_placement_2024'

# Global instances
mt_placement = None
data_generator = None
hosts = []
placement_history = []
system_stats = {
    'total_placements': 0,
    'successful_placements': 0,
    'avg_compliance_score': 0.0,
    'active_tenants': 0,
    'total_resources_allocated': {'cpu': 0, 'ram': 0}
}

def initialize_system():
    """Initialize the placement system with sample data"""
    global mt_placement, data_generator, hosts
    
    # Initialize multi-tenant placement system
    mt_placement = MultiTenantVMPlacement()
    
    # Generate realistic hosts
    data_generator = DataGenerator(num_hosts=20, seed=42)
    hosts = data_generator.host_specs.copy()
    
    # Add enterprise features to hosts
    regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'ap-north-1']
    for i, host in enumerate(hosts):
        host['encryption_at_rest'] = i < 16  # Most hosts have encryption
        host['region'] = regions[i % len(regions)]
        host['uptime_percentage'] = 99.5 + (i % 5) * 0.1
        host['last_maintenance'] = (datetime.now() - timedelta(days=(i * 7) % 90)).isoformat()
        host['compliance_certs'] = []
        
        # Assign compliance certifications based on host characteristics
        if i < 5:
            host['compliance_certs'].extend(['PCI_DSS', 'SOC2'])
        if i < 8:
            host['compliance_certs'].extend(['HIPAA', 'SOC2'])
        if i < 3:
            host['compliance_certs'].extend(['FedRAMP', 'ISO27001'])
        if not host['compliance_certs']:
            host['compliance_certs'].append('SOC2')  # All have at least SOC2
    
    print(f"✅ System initialized with {len(hosts)} hosts and {len(mt_placement.tenant_policies)} tenant policies")

@app.route('/')
def index():
    """Main dashboard page"""
    global system_stats
    
    # Update system stats
    update_system_stats()
    
    # Get recent placements
    recent_placements = placement_history[-10:] if placement_history else []
    
    # Get tenant summaries
    tenant_summaries = {}
    for tenant_id in mt_placement.tenant_policies.keys():
        if tenant_id in mt_placement.tenant_resource_usage:
            tenant_summaries[tenant_id] = mt_placement.get_tenant_usage_report(tenant_id)
    
    return render_template('dashboard.html', 
                         system_stats=system_stats,
                         recent_placements=recent_placements,
                         tenant_summaries=tenant_summaries,
                         total_hosts=len(hosts),
                         active_hosts=len([h for h in hosts if h.get('status', 'active') == 'active']))

@app.route('/hosts')
def hosts_view():
    """Host management and monitoring page"""
    # Calculate host utilizations
    for host in hosts:
        host['cpu_utilization'] = (host['current_cpu_usage'] / host['cpu_cores']) * 100
        host['ram_utilization'] = (host['current_ram_usage'] / host['ram_gb']) * 100
        host['overall_utilization'] = (host['cpu_utilization'] + host['ram_utilization']) / 2
        host['status'] = 'active' if host['overall_utilization'] < 90 else 'warning'
    
    return render_template('hosts.html', hosts=hosts)

@app.route('/tenants')
def tenants_view():
    """Tenant management page"""
    tenant_data = []
    
    for tenant_id, policy in mt_placement.tenant_policies.items():
        usage_report = {}
        if tenant_id in mt_placement.tenant_resource_usage:
            usage_report = mt_placement.get_tenant_usage_report(tenant_id)
        
        tenant_info = {
            'id': tenant_id,
            'name': policy.name,
            'data_classification': policy.data_classification.value,
            'compliance_frameworks': [cf.value for cf in policy.compliance_frameworks],
            'isolation_level': policy.isolation_level,
            'priority': policy.priority,
            'sla_requirement': policy.sla_requirement,
            'usage_report': usage_report
        }
        tenant_data.append(tenant_info)
    
    return render_template('tenants.html', tenants=tenant_data)

@app.route('/placement')
def placement_form():
    """VM placement request form"""
    return render_template('placement_form.html', 
                         tenant_policies=mt_placement.tenant_policies)

@app.route('/api/place_vm', methods=['POST'])
def api_place_vm():
    """API endpoint for VM placement requests"""
    try:
        data = request.json
        
        # Create VM request
        vm_request = {
            'vm_id': data.get('vm_id', f'vm-{uuid.uuid4().hex[:8]}'),
            'tenant_id': data['tenant_id'],
            'cpu_required': int(data['cpu_required']),
            'ram_required': int(data['ram_required']),
            'expected_runtime_hours': int(data.get('expected_runtime_hours', 24)),
            'priority': data.get('priority', 'medium'),
            'sla_requirement': float(data.get('sla_requirement', 0.99))
        }
        
        # Perform placement
        host_id, placement_info = mt_placement.place_vm_enterprise(vm_request, hosts)
        
        # Update host state
        if host_id != -1:
            selected_host = next(h for h in hosts if h['host_id'] == host_id)
            selected_host['current_cpu_usage'] += vm_request['cpu_required']
            selected_host['current_ram_usage'] += vm_request['ram_required']
        
        # Record placement in history
        placement_record = {
            'id': len(placement_history) + 1,
            'timestamp': datetime.now().isoformat(),
            'vm_request': vm_request,
            'result': {
                'host_id': host_id,
                'success': host_id != -1,
                'placement_info': placement_info
            }
        }
        placement_history.append(placement_record)
        
        # Update system stats
        update_system_stats()
        
        return jsonify({
            'success': True,
            'host_id': host_id,
            'placement_info': placement_info,
            'placement_record': placement_record
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/analytics')
def analytics_view():
    """Analytics and reporting page"""
    # Calculate analytics data
    analytics_data = calculate_analytics()
    
    return render_template('analytics.html', analytics=analytics_data)

@app.route('/audit')
def audit_view():
    """Audit trail and compliance reporting"""
    # Get audit logs
    audit_logs = mt_placement.placement_audit_log
    
    # Calculate compliance metrics
    compliance_metrics = calculate_compliance_metrics()
    
    return render_template('audit.html', 
                         audit_logs=audit_logs,
                         compliance_metrics=compliance_metrics,
                         placement_history=placement_history)

@app.route('/api/system_status')
def api_system_status():
    """API endpoint for real-time system status"""
    update_system_stats()
    
    # Calculate host utilization distribution
    host_utilizations = []
    for host in hosts:
        cpu_util = (host['current_cpu_usage'] / host['cpu_cores']) * 100
        ram_util = (host['current_ram_usage'] / host['ram_gb']) * 100
        host_utilizations.append({
            'host_id': host['host_id'],
            'cpu_utilization': cpu_util,
            'ram_utilization': ram_util,
            'overall_utilization': (cpu_util + ram_util) / 2
        })
    
    # Recent activity
    recent_activity = placement_history[-5:] if placement_history else []
    
    return jsonify({
        'system_stats': system_stats,
        'host_utilizations': host_utilizations,
        'recent_activity': recent_activity,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/tenant_usage/<tenant_id>')
def api_tenant_usage(tenant_id):
    """API endpoint for tenant usage details"""
    if tenant_id in mt_placement.tenant_resource_usage:
        usage_report = mt_placement.get_tenant_usage_report(tenant_id)
        return jsonify(usage_report)
    else:
        return jsonify({'error': 'Tenant not found'}), 404

@app.route('/demo')
def demo_page():
    """Demo page with sample workloads"""
    sample_workloads = [
        {
            'name': 'Healthcare Database',
            'tenant_id': 'healthcare-corp',
            'cpu_required': 8,
            'ram_required': 32,
            'priority': 'high',
            'description': 'Critical patient data processing system'
        },
        {
            'name': 'Financial Trading Engine',
            'tenant_id': 'fintech-startup', 
            'cpu_required': 16,
            'ram_required': 64,
            'priority': 'critical',
            'description': 'Real-time financial trading system'
        },
        {
            'name': 'Government Analytics',
            'tenant_id': 'government-agency',
            'cpu_required': 12,
            'ram_required': 48, 
            'priority': 'critical',
            'description': 'Classified security analysis workload'
        },
        {
            'name': 'E-commerce Frontend',
            'tenant_id': 'ecommerce-platform',
            'cpu_required': 4,
            'ram_required': 16,
            'priority': 'medium',
            'description': 'Customer-facing web application'
        }
    ]
    
    return render_template('demo.html', sample_workloads=sample_workloads)

@app.route('/api/run_demo', methods=['POST'])
def api_run_demo():
    """API endpoint to run demo placements"""
    try:
        demo_results = []
        
        sample_workloads = [
            {'name': 'Healthcare Database', 'tenant_id': 'healthcare-corp', 'cpu_required': 8, 'ram_required': 32, 'priority': 'high'},
            {'name': 'Financial Trading Engine', 'tenant_id': 'fintech-startup', 'cpu_required': 16, 'ram_required': 64, 'priority': 'critical'},
            {'name': 'Government Analytics', 'tenant_id': 'government-agency', 'cpu_required': 12, 'ram_required': 48, 'priority': 'critical'},
            {'name': 'E-commerce Frontend', 'tenant_id': 'ecommerce-platform', 'cpu_required': 4, 'ram_required': 16, 'priority': 'medium'}
        ]
        
        for workload in sample_workloads:
            vm_request = {
                'vm_id': f"demo-{workload['name'].lower().replace(' ', '-')}",
                'tenant_id': workload['tenant_id'],
                'cpu_required': workload['cpu_required'],
                'ram_required': workload['ram_required'],
                'expected_runtime_hours': 24,
                'priority': workload['priority']
            }
            
            host_id, placement_info = mt_placement.place_vm_enterprise(vm_request, hosts)
            
            if host_id != -1:
                selected_host = next(h for h in hosts if h['host_id'] == host_id)
                selected_host['current_cpu_usage'] += vm_request['cpu_required']
                selected_host['current_ram_usage'] += vm_request['ram_required']
            
            demo_results.append({
                'workload': workload['name'],
                'tenant_id': workload['tenant_id'],
                'host_id': host_id,
                'success': host_id != -1,
                'compliance_score': placement_info.get('compliance_score', 0),
                'placement_reason': placement_info.get('placement_reason', 'Failed')
            })
        
        update_system_stats()
        
        return jsonify({
            'success': True,
            'results': demo_results,
            'system_stats': system_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def update_system_stats():
    """Update global system statistics"""
    global system_stats
    
    successful_placements = sum(1 for p in placement_history if p['result']['success'])
    total_placements = len(placement_history)
    
    # Calculate average compliance score
    compliance_scores = [p['result']['placement_info'].get('compliance_score', 0) 
                        for p in placement_history if p['result']['success']]
    avg_compliance = np.mean(compliance_scores) if compliance_scores else 0
    
    # Calculate total resources allocated
    total_cpu = sum(usage.get('total_cpu', 0) for usage in mt_placement.tenant_resource_usage.values())
    total_ram = sum(usage.get('total_ram', 0) for usage in mt_placement.tenant_resource_usage.values())
    
    system_stats.update({
        'total_placements': total_placements,
        'successful_placements': successful_placements,
        'success_rate': (successful_placements / total_placements * 100) if total_placements > 0 else 0,
        'avg_compliance_score': avg_compliance,
        'active_tenants': len(mt_placement.tenant_resource_usage),
        'total_resources_allocated': {'cpu': total_cpu, 'ram': total_ram}
    })

def calculate_analytics():
    """Calculate analytics data for reporting"""
    if not placement_history:
        return {}
    
    # Placement success over time
    placement_timeline = []
    success_count = 0
    for i, placement in enumerate(placement_history):
        if placement['result']['success']:
            success_count += 1
        placement_timeline.append({
            'placement_number': i + 1,
            'success_rate': (success_count / (i + 1)) * 100,
            'timestamp': placement['timestamp']
        })
    
    # Tenant activity
    tenant_activity = {}
    for placement in placement_history:
        tenant_id = placement['vm_request']['tenant_id']
        if tenant_id not in tenant_activity:
            tenant_activity[tenant_id] = {'total': 0, 'successful': 0}
        tenant_activity[tenant_id]['total'] += 1
        if placement['result']['success']:
            tenant_activity[tenant_id]['successful'] += 1
    
    # Resource utilization trends
    resource_trends = []
    for i in range(min(len(placement_history), 20)):  # Last 20 placements
        total_cpu = sum(usage.get('total_cpu', 0) for usage in mt_placement.tenant_resource_usage.values())
        total_ram = sum(usage.get('total_ram', 0) for usage in mt_placement.tenant_resource_usage.values())
        resource_trends.append({
            'placement_number': len(placement_history) - 20 + i + 1,
            'total_cpu': total_cpu,
            'total_ram': total_ram
        })
    
    return {
        'placement_timeline': placement_timeline,
        'tenant_activity': tenant_activity,
        'resource_trends': resource_trends
    }

def calculate_compliance_metrics():
    """Calculate compliance-related metrics"""
    if not placement_history:
        return {}
    
    # Compliance framework usage
    framework_usage = {}
    for tenant_id, policy in mt_placement.tenant_policies.items():
        for framework in policy.compliance_frameworks:
            framework_name = framework.value
            if framework_name not in framework_usage:
                framework_usage[framework_name] = 0
            # Count placements for this tenant
            tenant_placements = sum(1 for p in placement_history 
                                  if p['vm_request']['tenant_id'] == tenant_id 
                                  and p['result']['success'])
            framework_usage[framework_name] += tenant_placements
    
    # Compliance scores distribution
    compliance_scores = [p['result']['placement_info'].get('compliance_score', 0) 
                        for p in placement_history if p['result']['success']]
    
    return {
        'framework_usage': framework_usage,
        'compliance_scores': compliance_scores,
        'perfect_compliance_rate': sum(1 for score in compliance_scores if score >= 1.0) / len(compliance_scores) * 100 if compliance_scores else 0
    }

if __name__ == '__main__':
    # Initialize the system
    initialize_system()
    
    # Run the web application
    print("🚀 Starting Enterprise VM Placement Web Application...")
    print("📱 Access the application at: http://localhost:5000")
    print("🏢 Features available:")
    print("   • Interactive Dashboard")
    print("   • Real-time VM Placement")
    print("   • Tenant Management")
    print("   • Host Monitoring")
    print("   • Analytics & Reporting")
    print("   • Audit Trails")
    print("   • Demo Scenarios")
    
    app.run(debug=True, host='0.0.0.0', port=5000)