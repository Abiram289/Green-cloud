#!/usr/bin/env python3
"""
Enterprise Multi-Tenant Placement Demo
Demonstrates the comprehensive enterprise VM placement system
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from multi_tenant_placement import MultiTenantVMPlacement, TenantPolicy, DataClassification, ComplianceFramework
from data_generator import DataGenerator

def create_enterprise_demo():
    """Create comprehensive enterprise demo with visualizations"""
    
    print("🏢 ENTERPRISE MULTI-TENANT VM PLACEMENT DEMO")
    print("=" * 70)
    
    # Initialize the multi-tenant system
    mt_placement = MultiTenantVMPlacement()
    
    # Generate realistic enterprise hosts
    data_gen = DataGenerator(num_hosts=15, seed=42)
    hosts = data_gen.host_specs.copy()
    
    # Add enterprise features to hosts
    regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
    for i, host in enumerate(hosts):
        host['encryption_at_rest'] = i < 12  # Most hosts have encryption
        host['region'] = regions[i % 4]
        host['compliance_certs'] = []
        
        # Assign compliance certifications
        if i < 4:  # First 4 hosts are PCI-DSS certified
            host['compliance_certs'].append('PCI_DSS')
        if i < 7:  # First 7 hosts are HIPAA compliant
            host['compliance_certs'].append('HIPAA')
        if i < 3:  # First 3 are government-grade
            host['compliance_certs'].append('FedRAMP')
        host['compliance_certs'].append('SOC2')  # All have SOC2
    
    print(f"🖥️  Generated {len(hosts)} enterprise hosts with compliance features")
    print(f"📋 Registered {len(mt_placement.tenant_policies)} tenant policies")
    print()
    
    # Create realistic enterprise workload scenarios
    enterprise_workloads = [
        {
            'name': 'Healthcare Patient Database',
            'tenant_id': 'healthcare-corp',
            'vm_id': 'patient-db-vm-01',
            'cpu_required': 8,
            'ram_required': 32,
            'expected_runtime_hours': 168,  # 1 week
            'priority': 'high',
            'description': 'Critical patient data processing system'
        },
        {
            'name': 'Financial Trading System', 
            'tenant_id': 'fintech-startup',
            'vm_id': 'trading-engine-vm-01',
            'cpu_required': 16,
            'ram_required': 64,
            'expected_runtime_hours': 24,
            'priority': 'critical',
            'description': 'Real-time financial trading engine'
        },
        {
            'name': 'Government Security Analysis',
            'tenant_id': 'government-agency',
            'vm_id': 'security-analysis-vm-01', 
            'cpu_required': 12,
            'ram_required': 48,
            'expected_runtime_hours': 72,
            'priority': 'critical',
            'description': 'Classified data analysis workload'
        },
        {
            'name': 'E-commerce Web Frontend',
            'tenant_id': 'ecommerce-platform',
            'vm_id': 'web-frontend-vm-01',
            'cpu_required': 4,
            'ram_required': 16,
            'expected_runtime_hours': 24,
            'priority': 'medium',
            'description': 'Customer-facing web application'
        },
        {
            'name': 'Healthcare Analytics',
            'tenant_id': 'healthcare-corp',
            'vm_id': 'analytics-vm-01',
            'cpu_required': 6,
            'ram_required': 24,
            'expected_runtime_hours': 48,
            'priority': 'medium',
            'description': 'Medical research analytics'
        },
        {
            'name': 'Financial Risk Assessment',
            'tenant_id': 'fintech-startup',
            'vm_id': 'risk-vm-01',
            'cpu_required': 4,
            'ram_required': 16,
            'expected_runtime_hours': 12,
            'priority': 'high',
            'description': 'Risk modeling and assessment'
        }
    ]
    
    print("🚀 ENTERPRISE WORKLOAD PLACEMENT SCENARIOS")
    print("-" * 50)
    
    placement_results = []
    
    for i, workload in enumerate(enterprise_workloads, 1):
        print(f"\n📊 Scenario {i}: {workload['name']}")
        print(f"   Tenant: {workload['tenant_id']} | Priority: {workload['priority']}")
        print(f"   Resources: {workload['cpu_required']} CPU, {workload['ram_required']} RAM")
        
        # Perform enterprise placement
        host_id, placement_info = mt_placement.place_vm_enterprise(workload, hosts)
        
        if host_id != -1:
            print(f"   ✅ Placed on Host {host_id}")
            print(f"   📋 Compliance Score: {placement_info['compliance_score']:.3f}")
            print(f"   🎯 Reason: {placement_info['placement_reason']}")
            print(f"   🔍 Alternatives Evaluated: {placement_info['alternatives_evaluated']}")
            
            # Update host state for next placement
            selected_host = next(h for h in hosts if h['host_id'] == host_id)
            selected_host['current_cpu_usage'] += workload['cpu_required']
            selected_host['current_ram_usage'] += workload['ram_required']
            
            placement_results.append({
                'workload': workload['name'],
                'tenant': workload['tenant_id'],
                'host_id': host_id,
                'compliance_score': placement_info['compliance_score'],
                'success': True
            })
        else:
            print(f"   ❌ Placement Failed: {placement_info['placement_reason']}")
            placement_results.append({
                'workload': workload['name'],
                'tenant': workload['tenant_id'], 
                'host_id': -1,
                'compliance_score': 0.0,
                'success': False
            })
    
    print("\n" + "=" * 70)
    print("📈 ENTERPRISE PLACEMENT ANALYSIS")
    print("=" * 70)
    
    # Generate comprehensive tenant reports
    print("\n🏢 TENANT RESOURCE UTILIZATION REPORTS")
    print("-" * 50)
    
    tenant_summaries = {}
    
    for tenant_id in mt_placement.tenant_policies.keys():
        if tenant_id in mt_placement.tenant_resource_usage:
            report = mt_placement.get_tenant_usage_report(tenant_id)
            tenant_summaries[tenant_id] = report
            
            print(f"\n🏢 {report['tenant_name']} ({tenant_id})")
            print(f"   📊 Resource Usage:")
            print(f"      • VMs Deployed: {report['usage_summary']['vm_count']}")
            print(f"      • Total CPU: {report['usage_summary']['total_cpu']} cores")
            print(f"      • Total RAM: {report['usage_summary']['total_ram']} GB")
            print(f"      • Hosts Used: {len(report['usage_summary'].get('hosts', {}))}")
            print(f"   💰 Cost Status: {report['cost_status']}")
            print(f"   ⚖️  Compliance: {report['compliance_status']}")
            if report['recommendations']:
                print(f"   💡 Recommendations: {'; '.join(report['recommendations'])}")
    
    # Performance metrics
    successful_placements = sum(1 for r in placement_results if r['success'])
    total_placements = len(placement_results)
    avg_compliance_score = np.mean([r['compliance_score'] for r in placement_results if r['success']])
    
    print(f"\n📊 OVERALL PERFORMANCE METRICS")
    print(f"   • Placement Success Rate: {successful_placements}/{total_placements} ({successful_placements/total_placements*100:.1f}%)")
    print(f"   • Average Compliance Score: {avg_compliance_score:.3f}")
    print(f"   • Tenants Served: {len(tenant_summaries)}")
    print(f"   • Total Workloads: {sum(s['usage_summary']['vm_count'] for s in tenant_summaries.values())}")
    
    # Export audit log
    audit_file = mt_placement.export_audit_log('results/enterprise_demo_audit.json')
    
    # Create visualization
    create_enterprise_visualizations(placement_results, tenant_summaries, hosts)
    
    print(f"\n🎉 Enterprise demo completed successfully!")
    print(f"📁 Audit log: {audit_file}")
    print(f"📊 Visualizations saved to results/enterprise_placement_analysis.png")
    
    return mt_placement, placement_results, tenant_summaries

def create_enterprise_visualizations(placement_results, tenant_summaries, hosts):
    """Create comprehensive enterprise visualizations"""
    
    # Create comprehensive figure
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('🏢 Enterprise Multi-Tenant VM Placement Analysis', fontsize=16, fontweight='bold')
    
    # Colors for tenants
    tenant_colors = {
        'healthcare-corp': '#e74c3c',      # Red
        'fintech-startup': '#3498db',      # Blue  
        'government-agency': '#2ecc71',    # Green
        'ecommerce-platform': '#f39c12'   # Orange
    }
    
    # 1. Placement Success by Tenant
    ax1 = axes[0, 0]
    tenant_success = {}
    for result in placement_results:
        tenant = result['tenant']
        if tenant not in tenant_success:
            tenant_success[tenant] = {'success': 0, 'total': 0}
        tenant_success[tenant]['total'] += 1
        if result['success']:
            tenant_success[tenant]['success'] += 1
    
    tenants = list(tenant_success.keys())
    success_rates = [tenant_success[t]['success'] / tenant_success[t]['total'] * 100 for t in tenants]
    colors = [tenant_colors.get(t, '#95a5a6') for t in tenants]
    
    bars1 = ax1.bar(range(len(tenants)), success_rates, color=colors, alpha=0.8)
    ax1.set_title('Placement Success Rate by Tenant', fontweight='bold')
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_xticks(range(len(tenants)))
    ax1.set_xticklabels([t.replace('-', '-\\n') for t in tenants], rotation=0)
    ax1.set_ylim(0, 105)
    
    # Add value labels
    for bar, rate in zip(bars1, success_rates):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 2. Resource Utilization by Tenant
    ax2 = axes[0, 1]
    tenant_names = []
    cpu_usage = []
    ram_usage = []
    
    for tenant_id, summary in tenant_summaries.items():
        tenant_names.append(summary['tenant_name'].split()[0])  # First word only
        cpu_usage.append(summary['usage_summary']['total_cpu'])
        ram_usage.append(summary['usage_summary']['total_ram'])
    
    x = np.arange(len(tenant_names))
    width = 0.35
    
    bars2a = ax2.bar(x - width/2, cpu_usage, width, label='CPU (cores)', color='#3498db', alpha=0.8)
    bars2b = ax2.bar(x + width/2, ram_usage, width, label='RAM (GB)', color='#e74c3c', alpha=0.8)
    
    ax2.set_title('Resource Usage by Tenant', fontweight='bold')
    ax2.set_ylabel('Resources')
    ax2.set_xticks(x)
    ax2.set_xticklabels(tenant_names)
    ax2.legend()
    
    # 3. Compliance Score Distribution
    ax3 = axes[0, 2]
    compliance_scores = [r['compliance_score'] for r in placement_results if r['success']]
    
    ax3.hist(compliance_scores, bins=10, color='#2ecc71', alpha=0.8, edgecolor='black')
    ax3.set_title('Compliance Score Distribution', fontweight='bold')
    ax3.set_xlabel('Compliance Score')
    ax3.set_ylabel('Frequency')
    ax3.axvline(np.mean(compliance_scores), color='red', linestyle='--', 
                label=f'Mean: {np.mean(compliance_scores):.3f}')
    ax3.legend()
    
    # 4. Host Utilization Heatmap
    ax4 = axes[1, 0]
    host_ids = [h['host_id'] for h in hosts[:10]]  # First 10 hosts
    cpu_utilization = [h['current_cpu_usage'] / h['cpu_cores'] * 100 for h in hosts[:10]]
    ram_utilization = [h['current_ram_usage'] / h['ram_gb'] * 100 for h in hosts[:10]]
    
    utilization_data = np.array([cpu_utilization, ram_utilization])
    im = ax4.imshow(utilization_data, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=100)
    
    ax4.set_title('Host Resource Utilization (%)', fontweight='bold')
    ax4.set_xticks(range(len(host_ids)))
    ax4.set_xticklabels([f'H{i}' for i in host_ids])
    ax4.set_yticks([0, 1])
    ax4.set_yticklabels(['CPU', 'RAM'])
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax4)
    cbar.set_label('Utilization (%)')
    
    # Add text annotations
    for i in range(2):
        for j in range(len(host_ids)):
            text = ax4.text(j, i, f'{utilization_data[i, j]:.1f}%',
                           ha="center", va="center", color="black", fontweight='bold')
    
    # 5. Workload Distribution by Host
    ax5 = axes[1, 1]
    host_workloads = {}
    for result in placement_results:
        if result['success']:
            host_id = result['host_id']
            tenant = result['tenant']
            if host_id not in host_workloads:
                host_workloads[host_id] = {}
            if tenant not in host_workloads[host_id]:
                host_workloads[host_id][tenant] = 0
            host_workloads[host_id][tenant] += 1
    
    # Create stacked bar chart
    hosts_used = sorted(host_workloads.keys())
    bottom = np.zeros(len(hosts_used))
    
    for tenant in tenant_colors.keys():
        tenant_counts = [host_workloads.get(h, {}).get(tenant, 0) for h in hosts_used]
        ax5.bar(range(len(hosts_used)), tenant_counts, bottom=bottom,
               label=tenant.replace('-', ' ').title(), 
               color=tenant_colors[tenant], alpha=0.8)
        bottom += tenant_counts
    
    ax5.set_title('Workload Distribution by Host', fontweight='bold')
    ax5.set_xlabel('Host ID')
    ax5.set_ylabel('Number of VMs')
    ax5.set_xticks(range(len(hosts_used)))
    ax5.set_xticklabels([f'Host {h}' for h in hosts_used])
    ax5.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 6. Enterprise Summary Metrics
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    # Calculate key metrics
    total_vms = sum(s['usage_summary']['vm_count'] for s in tenant_summaries.values())
    total_cpu = sum(s['usage_summary']['total_cpu'] for s in tenant_summaries.values())
    total_ram = sum(s['usage_summary']['total_ram'] for s in tenant_summaries.values())
    avg_compliance = np.mean([r['compliance_score'] for r in placement_results if r['success']])
    success_rate = sum(1 for r in placement_results if r['success']) / len(placement_results) * 100
    
    summary_text = f"""
🏢 ENTERPRISE SUMMARY

📊 Deployment Metrics:
   • Total VMs: {total_vms}
   • Total CPU: {total_cpu} cores
   • Total RAM: {total_ram} GB
   • Active Tenants: {len(tenant_summaries)}

✅ Performance Metrics:
   • Success Rate: {success_rate:.1f}%
   • Avg Compliance: {avg_compliance:.3f}
   • Hosts Utilized: {len(host_workloads)}

🔒 Compliance Status:
   • PCI-DSS: ✓ Active
   • HIPAA: ✓ Active  
   • FedRAMP: ✓ Active
   • SOC2: ✓ Active
    """
    
    ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, fontsize=11,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the visualization
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/enterprise_placement_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print("📊 Enterprise visualizations created successfully!")

if __name__ == "__main__":
    create_enterprise_demo()