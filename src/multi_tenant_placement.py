#!/usr/bin/env python3
"""
Multi-Tenant VM Placement Algorithm with Enterprise Constraints
Adds tenant isolation, compliance requirements, and enterprise features
"""

import sys
import os
sys.path.append('.')

import numpy as np
import pandas as pd
import json
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import hashlib

from ai_model import AIModel

class ComplianceFramework(Enum):
    """Supported compliance frameworks"""
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    SOX = "sox"
    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    FedRAMP = "fedramp"

class DataClassification(Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"

@dataclass
class TenantPolicy:
    """Tenant-specific placement policies"""
    tenant_id: str
    name: str
    data_classification: DataClassification
    compliance_frameworks: List[ComplianceFramework]
    allowed_regions: Optional[List[str]] = None
    blocked_regions: Optional[List[str]] = None
    isolation_level: str = "standard"  # standard, enhanced, dedicated
    max_cpu_per_host: Optional[float] = None
    max_ram_per_host: Optional[float] = None
    sla_requirement: float = 0.999
    cost_budget_limit: Optional[float] = None
    priority: str = "medium"  # low, medium, high, critical
    network_security_zones: List[str] = None
    encryption_required: bool = False
    audit_logging: bool = True

class MultiTenantVMPlacement:
    """
    Enterprise-grade multi-tenant VM placement with advanced constraints
    """
    
    def __init__(self):
        self.base_ai = AIModel()
        self.tenant_policies: Dict[str, TenantPolicy] = {}
        self.host_security_zones: Dict[int, Set[str]] = {}
        self.compliance_host_mapping: Dict[ComplianceFramework, Set[int]] = {}
        self.tenant_resource_usage: Dict[str, Dict] = {}
        self.placement_audit_log: List[Dict] = []
        
        self._initialize_compliance_mappings()
        self._load_tenant_policies()
    
    def _initialize_compliance_mappings(self):
        """Initialize compliance framework to host mappings"""
        # In production, this would be loaded from configuration
        self.compliance_host_mapping = {
            ComplianceFramework.PCI_DSS: {0, 1, 2, 3},  # Dedicated PCI hosts
            ComplianceFramework.HIPAA: {0, 1, 4, 5, 6},  # HIPAA-compliant hosts
            ComplianceFramework.SOX: {0, 1, 2, 7, 8},    # SOX-compliant hosts
            ComplianceFramework.GDPR: set(range(20)),     # All hosts (EU residency)
            ComplianceFramework.SOC2: set(range(15)),     # SOC2-certified hosts
            ComplianceFramework.ISO27001: set(range(12)), # ISO27001-certified hosts
            ComplianceFramework.FedRAMP: {0, 1, 2}        # Government-grade hosts
        }
        
        # Security zones (simulated)
        for host_id in range(20):
            zones = set()
            if host_id < 5:
                zones.add("dmz")
            if host_id < 10:
                zones.add("internal")
            if host_id < 15:
                zones.add("secure")
            if host_id < 3:
                zones.add("classified")
            
            self.host_security_zones[host_id] = zones
    
    def _load_tenant_policies(self):
        """Load tenant policies from configuration"""
        # Sample tenant policies - in production, load from database/config
        sample_policies = [
            TenantPolicy(
                tenant_id="healthcare-corp",
                name="HealthCare Corp",
                data_classification=DataClassification.RESTRICTED,
                compliance_frameworks=[ComplianceFramework.HIPAA, ComplianceFramework.SOC2],
                isolation_level="enhanced",
                max_cpu_per_host=0.5,  # Max 50% CPU per host
                sla_requirement=0.9999,
                priority="high",
                network_security_zones=["secure", "internal"],
                encryption_required=True
            ),
            TenantPolicy(
                tenant_id="fintech-startup",
                name="FinTech Startup",
                data_classification=DataClassification.CONFIDENTIAL,
                compliance_frameworks=[ComplianceFramework.PCI_DSS, ComplianceFramework.SOC2],
                isolation_level="standard",
                max_ram_per_host=0.6,  # Max 60% RAM per host
                sla_requirement=0.999,
                priority="medium",
                network_security_zones=["secure"],
                encryption_required=True
            ),
            TenantPolicy(
                tenant_id="government-agency",
                name="Government Agency",
                data_classification=DataClassification.TOP_SECRET,
                compliance_frameworks=[ComplianceFramework.FedRAMP, ComplianceFramework.ISO27001],
                isolation_level="dedicated",
                allowed_regions=["us-gov-west", "us-gov-east"],
                sla_requirement=0.99999,
                priority="critical",
                network_security_zones=["classified"],
                encryption_required=True
            ),
            TenantPolicy(
                tenant_id="ecommerce-platform",
                name="E-Commerce Platform", 
                data_classification=DataClassification.INTERNAL,
                compliance_frameworks=[ComplianceFramework.GDPR, ComplianceFramework.SOC2],
                isolation_level="standard",
                cost_budget_limit=1000.0,
                sla_requirement=0.995,
                priority="medium",
                network_security_zones=["internal", "dmz"]
            )
        ]
        
        for policy in sample_policies:
            self.tenant_policies[policy.tenant_id] = policy
    
    def register_tenant_policy(self, policy: TenantPolicy):
        """Register a new tenant policy"""
        self.tenant_policies[policy.tenant_id] = policy
        self.tenant_resource_usage[policy.tenant_id] = {
            'total_cpu': 0.0,
            'total_ram': 0.0,
            'total_cost': 0.0,
            'vm_count': 0,
            'last_updated': datetime.now()
        }
    
    def check_compliance_constraints(self, vm_request: Dict, host: Dict) -> Tuple[bool, List[str]]:
        """Check if placement meets compliance requirements"""
        tenant_id = vm_request.get('tenant_id', 'default')
        policy = self.tenant_policies.get(tenant_id)
        violations = []
        
        if not policy:
            return True, []  # No policy means no restrictions
        
        host_id = host['host_id']
        
        # 1. Compliance framework validation
        for framework in policy.compliance_frameworks:
            if host_id not in self.compliance_host_mapping.get(framework, set()):
                violations.append(f"Host {host_id} not certified for {framework.value}")
        
        # 2. Security zone validation
        if policy.network_security_zones:
            host_zones = self.host_security_zones.get(host_id, set())
            required_zones = set(policy.network_security_zones)
            if not required_zones.intersection(host_zones):
                violations.append(f"Host {host_id} not in required security zones: {required_zones}")
        
        # 3. Data classification validation
        if policy.data_classification == DataClassification.TOP_SECRET:
            if "classified" not in self.host_security_zones.get(host_id, set()):
                violations.append(f"TOP_SECRET data requires classified host")
        elif policy.data_classification == DataClassification.RESTRICTED:
            if "secure" not in self.host_security_zones.get(host_id, set()):
                violations.append(f"RESTRICTED data requires secure host")
        
        # 4. Encryption requirements
        if policy.encryption_required:
            if not host.get('encryption_at_rest', False):
                violations.append(f"Host {host_id} lacks required encryption")
        
        return len(violations) == 0, violations
    
    def check_isolation_constraints(self, vm_request: Dict, host: Dict) -> Tuple[bool, List[str]]:
        """Check tenant isolation requirements"""
        tenant_id = vm_request.get('tenant_id', 'default')
        policy = self.tenant_policies.get(tenant_id)
        violations = []
        
        if not policy:
            return True, []
        
        host_id = host['host_id']
        
        # 1. Dedicated isolation check
        if policy.isolation_level == "dedicated":
            # Check if host is already used by other tenants
            current_tenants = set()
            for other_tenant_id, usage in self.tenant_resource_usage.items():
                host_usage = usage.get('hosts', {}).get(host_id, {})
                if isinstance(host_usage, dict) and host_usage.get('vm_count', 0) > 0:
                    current_tenants.add(other_tenant_id)
            
            if current_tenants and tenant_id not in current_tenants:
                violations.append(f"Dedicated isolation violated: host {host_id} used by other tenants")
        
        # 2. Resource limits per host
        tenant_usage = self.tenant_resource_usage.get(tenant_id, {})
        host_usage = tenant_usage.get('hosts', {}).get(host_id, {})
        current_cpu_on_host = host_usage.get('cpu', 0) if isinstance(host_usage, dict) else 0
        current_ram_on_host = host_usage.get('ram', 0) if isinstance(host_usage, dict) else 0
        
        if policy.max_cpu_per_host:
            new_cpu_usage = (current_cpu_on_host + vm_request['cpu_required']) / host['cpu_cores']
            if new_cpu_usage > policy.max_cpu_per_host:
                violations.append(f"CPU limit exceeded: {new_cpu_usage:.2%} > {policy.max_cpu_per_host:.2%}")
        
        if policy.max_ram_per_host:
            new_ram_usage = (current_ram_on_host + vm_request['ram_required']) / host['ram_gb']
            if new_ram_usage > policy.max_ram_per_host:
                violations.append(f"RAM limit exceeded: {new_ram_usage:.2%} > {policy.max_ram_per_host:.2%}")
        
        return len(violations) == 0, violations
    
    def check_cost_constraints(self, vm_request: Dict, host: Dict) -> Tuple[bool, List[str]]:
        """Check cost budget constraints"""
        tenant_id = vm_request.get('tenant_id', 'default')
        policy = self.tenant_policies.get(tenant_id)
        violations = []
        
        if not policy or not policy.cost_budget_limit:
            return True, []
        
        # Calculate estimated cost
        if hasattr(self.base_ai, 'calculate_cost'):
            estimated_cost = self.base_ai.calculate_cost(vm_request, host)
        else:
            # Fallback cost calculation
            cpu_util = vm_request['cpu_required'] / host['cpu_cores']
            usage_factor = 1 + 0.5 * cpu_util
            estimated_cost = host['cost_per_hour'] * usage_factor * vm_request.get('expected_runtime_hours', 24)
        
        tenant_usage = self.tenant_resource_usage.get(tenant_id, {})
        current_cost = tenant_usage.get('total_cost', 0)
        
        if current_cost + estimated_cost > policy.cost_budget_limit:
            violations.append(f"Budget exceeded: ${current_cost + estimated_cost:.2f} > ${policy.cost_budget_limit:.2f}")
        
        return len(violations) == 0, violations
    
    def calculate_compliance_score(self, vm_request: Dict, host: Dict) -> float:
        """Calculate compliance score for placement (0-1, higher is better)"""
        tenant_id = vm_request.get('tenant_id', 'default')
        policy = self.tenant_policies.get(tenant_id)
        
        if not policy:
            return 1.0  # No policy = perfect compliance
        
        score = 1.0
        host_id = host['host_id']
        
        # Compliance framework score
        frameworks_met = 0
        for framework in policy.compliance_frameworks:
            if host_id in self.compliance_host_mapping.get(framework, set()):
                frameworks_met += 1
        
        if policy.compliance_frameworks:
            compliance_ratio = frameworks_met / len(policy.compliance_frameworks)
            score *= compliance_ratio
        
        # Security zone score
        if policy.network_security_zones:
            host_zones = self.host_security_zones.get(host_id, set())
            required_zones = set(policy.network_security_zones)
            zone_overlap = len(required_zones.intersection(host_zones))
            zone_score = zone_overlap / len(required_zones)
            score *= zone_score
        
        # Data classification score
        classification_score = 1.0
        if policy.data_classification == DataClassification.TOP_SECRET:
            if "classified" not in self.host_security_zones.get(host_id, set()):
                classification_score = 0.0
        elif policy.data_classification == DataClassification.RESTRICTED:
            if "secure" not in self.host_security_zones.get(host_id, set()):
                classification_score = 0.5
        
        score *= classification_score
        
        return max(0.0, min(1.0, score))
    
    def place_vm_enterprise(self, vm_request: Dict, hosts: List[Dict]) -> Tuple[int, Dict]:
        """
        Enterprise VM placement with multi-tenant constraints
        Returns: (host_id, placement_info)
        """
        tenant_id = vm_request.get('tenant_id', 'default')
        policy = self.tenant_policies.get(tenant_id)
        
        placement_info = {
            'tenant_id': tenant_id,
            'timestamp': datetime.now(),
            'compliance_checks': [],
            'violations': [],
            'placement_reason': '',
            'compliance_score': 0.0
        }
        
        # Filter hosts based on enterprise constraints
        enterprise_feasible_hosts = []
        
        for host in hosts:
            # Basic feasibility
            if not self.base_ai.can_place_vm(vm_request, host):
                continue
            
            # Enterprise constraint checks
            compliance_ok, compliance_violations = self.check_compliance_constraints(vm_request, host)
            isolation_ok, isolation_violations = self.check_isolation_constraints(vm_request, host)
            cost_ok, cost_violations = self.check_cost_constraints(vm_request, host)
            
            all_violations = compliance_violations + isolation_violations + cost_violations
            
            if compliance_ok and isolation_ok and cost_ok:
                # Calculate enterprise scores
                compliance_score = self.calculate_compliance_score(vm_request, host)
                
                # Get base AI score
                base_scores = self.base_ai.calculate_multi_objective_score(vm_request, host, hosts)
                base_composite = base_scores['composite_score'] if base_scores['feasible'] else 0.0
                
                # Priority weighting
                priority_weight = {
                    'low': 0.8,
                    'medium': 1.0, 
                    'high': 1.2,
                    'critical': 1.5
                }.get(policy.priority if policy else 'medium', 1.0)
                
                # Enterprise composite score
                enterprise_score = (
                    0.4 * base_composite +           # Base AI optimization
                    0.3 * compliance_score +         # Compliance requirements
                    0.2 * priority_weight +          # Tenant priority
                    0.1 * (1 - len(all_violations) / 10)  # Violation penalty
                )
                
                enterprise_feasible_hosts.append({
                    'host_id': host['host_id'],
                    'enterprise_score': enterprise_score,
                    'compliance_score': compliance_score,
                    'base_score': base_composite,
                    'violations': all_violations,
                    'host': host
                })
        
        # Select best enterprise host
        if not enterprise_feasible_hosts:
            # No enterprise-compliant hosts available
            placement_info['placement_reason'] = 'No compliant hosts available'
            placement_info['violations'] = ['No hosts meet enterprise constraints']
            return -1, placement_info
        
        # Sort by enterprise score
        enterprise_feasible_hosts.sort(key=lambda x: x['enterprise_score'], reverse=True)
        best_placement = enterprise_feasible_hosts[0]
        
        # Update tenant usage tracking
        self._update_tenant_usage(tenant_id, vm_request, best_placement['host'])
        
        # Create audit log entry
        audit_entry = {
            'placement_id': self._generate_placement_id(vm_request),
            'tenant_id': tenant_id,
            'vm_request': vm_request.copy(),
            'selected_host_id': best_placement['host_id'],
            'enterprise_score': best_placement['enterprise_score'],
            'compliance_score': best_placement['compliance_score'],
            'policy_applied': policy.name if policy else 'Default',
            'timestamp': datetime.now(),
            'alternatives_count': len(enterprise_feasible_hosts)
        }
        self.placement_audit_log.append(audit_entry)
        
        # Fill placement info
        placement_info.update({
            'placement_reason': f'Best enterprise score: {best_placement["enterprise_score"]:.3f}',
            'compliance_score': best_placement['compliance_score'],
            'alternatives_evaluated': len(enterprise_feasible_hosts),
            'audit_id': audit_entry['placement_id']
        })
        
        return best_placement['host_id'], placement_info
    
    def _update_tenant_usage(self, tenant_id: str, vm_request: Dict, host: Dict):
        """Update tenant resource usage tracking"""
        if tenant_id not in self.tenant_resource_usage:
            self.tenant_resource_usage[tenant_id] = {
                'total_cpu': 0.0,
                'total_ram': 0.0,
                'total_cost': 0.0,
                'vm_count': 0,
                'hosts': {},
                'last_updated': datetime.now()
            }
        
        usage = self.tenant_resource_usage[tenant_id]
        host_id = host['host_id']
        
        # Update totals
        usage['total_cpu'] += vm_request['cpu_required']
        usage['total_ram'] += vm_request['ram_required']
        usage['vm_count'] += 1
        
        # Update per-host usage
        if host_id not in usage['hosts']:
            usage['hosts'][host_id] = {'cpu': 0.0, 'ram': 0.0, 'vm_count': 0}
        
        usage['hosts'][host_id]['cpu'] += vm_request['cpu_required']
        usage['hosts'][host_id]['ram'] += vm_request['ram_required']
        usage['hosts'][host_id]['vm_count'] += 1
        usage['last_updated'] = datetime.now()
    
    def _generate_placement_id(self, vm_request: Dict) -> str:
        """Generate unique placement ID for audit trail"""
        content = f"{vm_request.get('vm_id', 'unknown')}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def get_tenant_usage_report(self, tenant_id: str) -> Dict:
        """Generate tenant resource usage report"""
        if tenant_id not in self.tenant_resource_usage:
            return {'error': f'Tenant {tenant_id} not found'}
        
        usage = self.tenant_resource_usage[tenant_id]
        policy = self.tenant_policies.get(tenant_id)
        
        report = {
            'tenant_id': tenant_id,
            'tenant_name': policy.name if policy else 'Unknown',
            'usage_summary': usage.copy(),
            'compliance_status': 'compliant',
            'cost_status': 'within_budget',
            'recommendations': []
        }
        
        # Cost analysis
        if policy and policy.cost_budget_limit:
            utilization = usage['total_cost'] / policy.cost_budget_limit
            report['cost_utilization'] = utilization
            if utilization > 0.9:
                report['cost_status'] = 'approaching_limit'
                report['recommendations'].append('Consider cost optimization or budget increase')
            elif utilization > 1.0:
                report['cost_status'] = 'over_budget'
                report['recommendations'].append('Immediate cost reduction required')
        
        # Resource distribution analysis
        host_count = len(usage.get('hosts', {}))
        if host_count > 0:
            avg_cpu_per_host = usage['total_cpu'] / host_count
            avg_ram_per_host = usage['total_ram'] / host_count
            
            report['resource_distribution'] = {
                'hosts_used': host_count,
                'avg_cpu_per_host': avg_cpu_per_host,
                'avg_ram_per_host': avg_ram_per_host
            }
            
            if policy and policy.isolation_level == 'dedicated' and host_count > 5:
                report['recommendations'].append('Consider consolidating to fewer dedicated hosts')
        
        return report
    
    def export_audit_log(self, output_file: str = 'results/enterprise_audit_log.json'):
        """Export placement audit log for compliance reporting"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        audit_export = {
            'export_timestamp': datetime.now().isoformat(),
            'total_placements': len(self.placement_audit_log),
            'placements': self.placement_audit_log.copy()
        }
        
        # Convert datetime objects to ISO strings
        for placement in audit_export['placements']:
            if isinstance(placement.get('timestamp'), datetime):
                placement['timestamp'] = placement['timestamp'].isoformat()
        
        with open(output_file, 'w') as f:
            json.dump(audit_export, f, indent=2, default=str)
        
        print(f"📋 Audit log exported to {output_file}")
        return output_file


def test_multi_tenant_placement():
    """Test the multi-tenant placement system"""
    print("🏢 Testing Multi-Tenant Enterprise Placement")
    print("=" * 60)
    
    # Initialize multi-tenant system
    mt_placement = MultiTenantVMPlacement()
    
    # Create test hosts with enterprise features
    from data_generator import DataGenerator
    data_gen = DataGenerator(num_hosts=10, seed=42)
    hosts = data_gen.host_specs.copy()
    
    # Add enterprise features to hosts
    for i, host in enumerate(hosts):
        host['encryption_at_rest'] = i < 8  # Most hosts have encryption
        host['region'] = ['us-east', 'us-west', 'eu-west'][i % 3]
    
    # Test different tenant scenarios
    test_scenarios = [
        {
            'tenant_id': 'healthcare-corp',
            'vm_id': 'vm-health-001',
            'cpu_required': 4,
            'ram_required': 8,
            'expected_runtime_hours': 48,
            'priority': 'high'
        },
        {
            'tenant_id': 'fintech-startup', 
            'vm_id': 'vm-fintech-001',
            'cpu_required': 2,
            'ram_required': 4,
            'expected_runtime_hours': 24,
            'priority': 'medium'
        },
        {
            'tenant_id': 'government-agency',
            'vm_id': 'vm-gov-001', 
            'cpu_required': 8,
            'ram_required': 16,
            'expected_runtime_hours': 168,
            'priority': 'critical'
        },
        {
            'tenant_id': 'ecommerce-platform',
            'vm_id': 'vm-ecom-001',
            'cpu_required': 2,
            'ram_required': 8,
            'expected_runtime_hours': 12,
            'priority': 'medium'
        }
    ]
    
    print(f"🧪 Testing {len(test_scenarios)} enterprise placement scenarios...")
    print()
    
    for i, vm_request in enumerate(test_scenarios, 1):
        print(f"📋 Scenario {i}: {vm_request['tenant_id']} ({vm_request['priority']} priority)")
        
        host_id, placement_info = mt_placement.place_vm_enterprise(vm_request, hosts)
        
        if host_id != -1:
            print(f"✅ Placed on Host {host_id}")
            print(f"   Compliance Score: {placement_info['compliance_score']:.3f}")
            print(f"   Reason: {placement_info['placement_reason']}")
            print(f"   Alternatives: {placement_info['alternatives_evaluated']}")
            print(f"   Audit ID: {placement_info['audit_id']}")
        else:
            print(f"❌ Placement Failed")
            print(f"   Reason: {placement_info['placement_reason']}")
            print(f"   Violations: {placement_info['violations']}")
        print()
    
    # Generate tenant usage reports
    print("📊 TENANT USAGE REPORTS")
    print("-" * 40)
    for tenant_id in mt_placement.tenant_policies.keys():
        if tenant_id in mt_placement.tenant_resource_usage:
            report = mt_placement.get_tenant_usage_report(tenant_id)
            print(f"\n🏢 {report['tenant_name']} ({tenant_id})")
            print(f"   VMs: {report['usage_summary']['vm_count']}")
            print(f"   CPU: {report['usage_summary']['total_cpu']} cores")
            print(f"   RAM: {report['usage_summary']['total_ram']} GB")
            print(f"   Hosts: {report['usage_summary'].get('hosts', {}).keys()}")
            print(f"   Status: {report['cost_status']}")
            if report['recommendations']:
                print(f"   Recommendations: {', '.join(report['recommendations'])}")
    
    # Export audit log
    audit_file = mt_placement.export_audit_log()
    
    print(f"\n🎉 Multi-tenant testing completed!")
    print(f"📁 Audit log: {audit_file}")
    
    return mt_placement


if __name__ == "__main__":
    test_multi_tenant_placement()