# Quick Start Guide

## 🚀 **Most Common Commands**

### **Generate Complete Visualization Suite**
```powershell
python comprehensive_visualization.py
```
**Output:** `results/executive_dashboard.png`, `results/technical_analysis.png`, `results/comparison_matrix.png`

### **Debug AI Algorithm Issues**
```powershell
python debug_ai_placement.py
```
**Output:** Console diagnostics for feature mapping and AI prediction quality

### **Test Improved AI Performance**
```powershell
python improved_ai_algorithm.py
```
**Output:** Console test results showing energy/cost improvements

### **Check System Environment**
```powershell
python check_system.py
```
**Output:** Python version, package status, model file existence

## 📊 **Understanding the Results**

### **Performance Ranking (results/performance_ranking.csv)**
- **Column 1:** Algorithm name
- **Column 2:** Composite score (higher = better)
- **Columns 3-6:** Normalized scores for Success/Efficiency/Cost/Energy

### **Benchmark Results (results/benchmark_results.json)**
- **Per algorithm arrays:** energy_consumption, cost, cpu_utilization, ram_utilization
- **Success metrics:** success_count, placement_times, efficiency_scores

## 🎯 **Key Files to Know**

| File | Purpose | When to Use |
|------|---------|-------------|
| `comprehensive_visualization.py` | Main visualization generator | Creating presentations/reports |
| `improved_ai_algorithm.py` | Production-ready AI engine | Best performance + reliability |
| `src/enhanced_algorithms.py` | Original hybrid AI | Research/comparison |
| `src/placement_algorithms.py` | Traditional algorithms | Baseline comparisons |
| `results/executive_dashboard.png` | Business-level metrics | Executive presentations |
| `results/technical_analysis.png` | Engineering deep-dive | Technical reviews |
| `models/hybrid_ai_predictor.pkl` | Main AI model | Used by all AI algorithms |

## ⚡ **Common Issues & Quick Fixes**

| Problem | Solution |
|---------|----------|
| `ImportError: cannot import name 'FirstFitAlgorithm'` | Use `FirstFitPlacement` instead |
| AI predictions all ~0.0 | Run `debug_ai_placement.py` to diagnose |
| Seaborn import hangs | Use `comprehensive_visualization.py` instead |
| Results look unrealistic | Increase `num_scenarios` in visualization script |
| Missing model files | Check `models/` directory exists with `.pkl` files |

## 🔄 **Typical Workflow**

1. **Check system:** `python check_system.py`
2. **Generate visuals:** `python comprehensive_visualization.py`
3. **Debug if needed:** `python debug_ai_placement.py`
4. **Review results:** Open `results/executive_dashboard.png`

## 📈 **Expected Performance**

| Algorithm | Typical Energy | Typical Cost | Success Rate |
|-----------|---------------|--------------|--------------|
| **Improved AI** | ~94W | ~$22 | 100% |
| **LB-Best-Fit** | ~150-300W | ~$50-100 | 100% |
| **Traditional** | ~400-600W | ~$100-200 | 95-100% |

*Results vary by scenario distribution and host configurations*