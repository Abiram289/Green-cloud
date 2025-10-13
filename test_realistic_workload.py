#!/usr/bin/env python3
import requests
import json

try:
    r = requests.get('http://localhost:5000/api/detailed_comparison')
    data = r.json()
    
    print("=== SUCCESS RATES ===")
    for alg in data['results']:
        success_rate = data['results'][alg]['success_rate']
        print(f"{alg}: {success_rate:.1%}")
    
    print("\n=== SLA VIOLATIONS ===")
    for alg in data['results']:
        sla_violations = data['results'][alg].get('sla_violations', data['results'][alg].get('failed_placements', 0))
        print(f"{alg}: {sla_violations}")
    
    print(f"\n=== TOTAL VM REQUESTS ===")
    print(f"Number of VMs generated: {len(data.get('test_config', {}).get('vm_requests', 'Unknown'))}")
    
    if 'detailed_metrics' in data and 'AI Model' in data['detailed_metrics']:
        print("\n=== AI Model Debug Info ===")
        for item in data['detailed_metrics']['AI Model']:
            print(item)
    
except Exception as e:
    print(f"Error: {e}")
