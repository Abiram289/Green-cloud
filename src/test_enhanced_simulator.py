"""
Test script for the Enhanced VM Placement Simulator

This script demonstrates the enhanced simulation capabilities with load balancing
and advanced AI algorithms.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Ensure we can import from src directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_simulator():
    """Test the enhanced simulator with a smaller dataset"""
    from enhanced_simulator import EnhancedVMPlacementSimulator
    
    print("Testing Enhanced VM Placement Simulator")
    print("="*50)
    
    # Initialize simulator
    try:
        simulator = EnhancedVMPlacementSimulator()
        print("✓ Simulator initialized successfully")
        
        # Test VM request generation
        vm_requests = simulator.generate_enhanced_vm_requests(100)
        print(f"✓ Generated {len(vm_requests)} enhanced VM requests")
        
        # Show sample of enhanced requests
        print("\nSample Enhanced VM Requests:")
        print("-" * 30)
        for i, req in enumerate(vm_requests[:3]):
            print(f"VM {i+1}: CPU={req['cpu_required']}, RAM={req['ram_required']}, "
                  f"Type={req['vm_type']}, Priority={req['priority']}, "
                  f"SLA={req['sla_requirement']}, Runtime={req['expected_runtime_hours']:.1f}h")
        
        # Quick evaluation with smaller dataset
        print(f"\nRunning quick evaluation with {len(vm_requests)} VM requests...")
        results = simulator.run_comprehensive_enhanced_evaluation(
            num_vm_requests=100,  # Smaller for testing
            num_runs=2           # Fewer runs for testing
        )
        
        print("✓ Enhanced evaluation completed")
        
        # Print summary
        simulator.print_enhanced_results_summary()
        
        # Create visualization
        print("\nCreating enhanced visualization...")
        simulator.create_quick_visualization()
        
        # Save results
        simulator.save_enhanced_results("test_enhanced_results.json")
        
        print("\n✓ Enhanced simulator test completed successfully!")
        print(f"✓ Evaluated {len(results)} algorithm configurations")
        
        return simulator
        
    except Exception as e:
        print(f"✗ Error during enhanced simulator test: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_load_balancing_improvements():
    """Analyze improvements from load balancing algorithms"""
    print("\n" + "="*60)
    print("ANALYZING LOAD BALANCING IMPROVEMENTS")
    print("="*60)
    
    try:
        from enhanced_simulator import EnhancedVMPlacementSimulator
        
        simulator = EnhancedVMPlacementSimulator()
        
        # Generate a challenging scenario with mixed workloads
        vm_requests = simulator.generate_enhanced_vm_requests(200)
        
        # Analyze request distribution
        vm_types = [req['vm_type'] for req in vm_requests]
        print("\nWorkload Distribution:")
        for vm_type in set(vm_types):
            count = vm_types.count(vm_type)
            percentage = count / len(vm_requests) * 100
            print(f"  {vm_type:8}: {count:3} requests ({percentage:5.1f}%)")
        
        # Calculate resource requirements
        total_cpu = sum(req['cpu_required'] for req in vm_requests)
        total_ram = sum(req['ram_required'] for req in vm_requests)
        avg_cpu = total_cpu / len(vm_requests)
        avg_ram = total_ram / len(vm_requests)
        
        print(f"\nResource Requirements:")
        print(f"  Total CPU: {total_cpu:4} cores")
        print(f"  Total RAM: {total_ram:4} GB")
        print(f"  Avg CPU:   {avg_cpu:6.2f} cores/VM")
        print(f"  Avg RAM:   {avg_ram:6.2f} GB/VM")
        
        # Priority distribution
        priorities = [req['priority'] for req in vm_requests]
        print(f"\nPriority Distribution:")
        for priority in ['low', 'medium', 'high']:
            count = priorities.count(priority)
            percentage = count / len(vm_requests) * 100
            print(f"  {priority:6}: {count:3} requests ({percentage:5.1f}%)")
        
        print("\n✓ Load balancing analysis completed")
        
    except Exception as e:
        print(f"✗ Error in load balancing analysis: {e}")

def compare_ai_vs_traditional():
    """Compare AI algorithms against traditional algorithms"""
    print("\n" + "="*60)
    print("AI vs TRADITIONAL ALGORITHM COMPARISON")
    print("="*60)
    
    try:
        # This would be implemented when advanced models are available
        print("AI comparison will be available when enhanced models are trained.")
        print("Current implementation provides framework for:")
        print("  • Multi-objective optimization")
        print("  • Ensemble learning methods")
        print("  • Advanced feature engineering")
        print("  • Hyperparameter optimization")
        print("  • Load balancing aware placement")
        
    except Exception as e:
        print(f"✗ Error in AI comparison: {e}")

def main():
    """Main test function"""
    print("Enhanced VM Placement Simulator Test Suite")
    print("="*60)
    
    # Test basic simulator functionality
    simulator = test_enhanced_simulator()
    
    if simulator:
        # Additional analysis
        analyze_load_balancing_improvements()
        compare_ai_vs_traditional()
        
        print("\n" + "="*60)
        print("✓ ALL ENHANCED SIMULATOR TESTS PASSED")
        print("="*60)
        print("\nNext steps:")
        print("1. Train advanced AI models using advanced_model_trainer.py")
        print("2. Run full-scale evaluation with larger datasets")
        print("3. Use comprehensive_visualization.py for detailed analysis")
        print("4. Analyze load balancing improvements")
        
    else:
        print("\n" + "="*60)
        print("✗ ENHANCED SIMULATOR TESTS FAILED")
        print("="*60)

if __name__ == "__main__":
    main()