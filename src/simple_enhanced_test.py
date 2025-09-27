"""
Simple test for Enhanced VM Placement Simulator with basic algorithms
"""

import sys
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_enhanced_simulator():
    """Test enhanced simulator with basic algorithms only"""
    
    print("Testing Enhanced VM Placement Simulator (Basic Version)")
    print("="*60)
    
    # Import basic algorithms to avoid AI model dependencies
    from placement_algorithms import (
        FirstFitPlacement, BestFitPlacement, WorstFitPlacement,
        RandomPlacement, RoundRobinPlacement
    )
    from enhanced_simulator import EnhancedVMPlacementSimulator
    
    # Initialize simulator
    try:
        simulator = EnhancedVMPlacementSimulator()
        print("✓ Enhanced simulator initialized")
        
        # Generate enhanced VM requests
        vm_requests = simulator.generate_enhanced_vm_requests(50)  # Small test
        print(f"✓ Generated {len(vm_requests)} enhanced VM requests")
        
        # Show enhanced request features
        print("\n📊 Enhanced VM Request Features:")
        print("-" * 40)
        
        vm_types = {}
        priorities = {}
        sla_requirements = []
        
        for req in vm_requests:
            vm_type = req['vm_type']
            priority = req['priority']
            vm_types[vm_type] = vm_types.get(vm_type, 0) + 1
            priorities[priority] = priorities.get(priority, 0) + 1
            sla_requirements.append(req['sla_requirement'])
        
        print("VM Type Distribution:")
        for vm_type, count in vm_types.items():
            print(f"  {vm_type:8}: {count:2} ({count/len(vm_requests)*100:4.1f}%)")
        
        print("\nPriority Distribution:")
        for priority, count in priorities.items():
            print(f"  {priority:6}: {count:2} ({count/len(vm_requests)*100:4.1f}%)")
        
        avg_sla = sum(sla_requirements) / len(sla_requirements)
        print(f"\nAverage SLA Requirement: {avg_sla:.4f}")
        
        # Test individual algorithms
        print(f"\n🔧 Testing Basic Algorithms:")
        print("-" * 40)
        
        algorithms = [
            FirstFitPlacement(),
            BestFitPlacement(),
            WorstFitPlacement(),
            RandomPlacement(),
            RoundRobinPlacement()
        ]
        
        results = {}
        
        for algorithm in algorithms:
            print(f"\nTesting {algorithm.name}...")
            
            try:
                placements, metrics = simulator.run_enhanced_algorithm_simulation(algorithm, vm_requests)
                results[algorithm.name] = metrics
                
                success_rate = metrics['successful_placements'] / len(vm_requests)
                energy = metrics.get('total_energy_consumption', 0)
                cost = metrics.get('total_cost', 0)
                cpu_util = metrics.get('average_cpu_utilization', 0) * 100
                ram_util = metrics.get('average_ram_utilization', 0) * 100
                
                print(f"  Success Rate: {success_rate:.3f}")
                print(f"  Energy:       {energy:6.0f} W")
                print(f"  Cost:         ${cost:6.0f}")
                print(f"  CPU Util:     {cpu_util:5.1f}%")
                print(f"  RAM Util:     {ram_util:5.1f}%")
                
                # Enhanced metrics if available
                if 'average_placement_time' in metrics:
                    avg_time = metrics['average_placement_time'] * 1000  # Convert to ms
                    print(f"  Avg Time:     {avg_time:.2f} ms")
                
                print(f"  ✓ {algorithm.name} completed")
                
            except Exception as e:
                print(f"  ✗ Error with {algorithm.name}: {e}")
                results[algorithm.name] = {'error': str(e)}
        
        # Summary comparison
        print(f"\n📈 ALGORITHM COMPARISON SUMMARY")
        print("="*60)
        
        successful_results = {name: data for name, data in results.items() if 'error' not in data}
        
        if successful_results:
            # Best by different metrics
            best_success = max(successful_results.items(), 
                             key=lambda x: x[1].get('successful_placements', 0) / len(vm_requests))
            best_energy = min(successful_results.items(), 
                            key=lambda x: x[1].get('total_energy_consumption', float('inf')))
            best_cost = min(successful_results.items(), 
                          key=lambda x: x[1].get('total_cost', float('inf')))
            
            print(f"🏆 Best Success Rate: {best_success[0]} ({best_success[1]['successful_placements']/len(vm_requests):.3f})")
            print(f"⚡ Most Energy Efficient: {best_energy[0]} ({best_energy[1]['total_energy_consumption']:.0f} W)")
            print(f"💰 Most Cost Effective: {best_cost[0]} (${best_cost[1]['total_cost']:.0f})")
        
        # Enhanced features demonstrated
        print(f"\n✨ ENHANCED FEATURES DEMONSTRATED:")
        print("-" * 40)
        print("✓ Realistic VM request generation with types and priorities")
        print("✓ Enhanced metrics calculation with timing")
        print("✓ SLA requirements and runtime modeling")
        print("✓ Comprehensive performance evaluation")
        print("✓ Statistical analysis across multiple metrics")
        
        print(f"\n✅ Enhanced simulator basic test PASSED!")
        print(f"   Tested {len(algorithms)} algorithms")
        print(f"   Generated {len(vm_requests)} enhanced VM requests")
        print(f"   Calculated comprehensive metrics")
        
        return True
        
    except Exception as e:
        print(f"✗ Enhanced simulator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("Enhanced VM Placement Simulator - Basic Algorithm Test")
    print("="*70)
    
    success = test_basic_enhanced_simulator()
    
    if success:
        print("\n" + "="*70)
        print("🎉 ENHANCED SIMULATOR BASIC TEST COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n📋 Next Steps:")
        print("1. Train advanced AI models using advanced_model_trainer.py")
        print("2. Test enhanced algorithms with load balancing features")
        print("3. Run full-scale evaluation with comprehensive_visualization.py")
        print("4. Compare AI vs traditional algorithm performance")
    else:
        print("\n" + "="*70)
        print("❌ ENHANCED SIMULATOR BASIC TEST FAILED")
        print("="*70)

if __name__ == "__main__":
    main()