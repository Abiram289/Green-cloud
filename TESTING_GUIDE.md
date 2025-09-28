# 🧪 Enhanced VM Placement System - Testing Guide

This guide provides instructions for verifying the functionality and performance of the project, with a focus on the primary user interface: the web dashboard.

---

## ✅ **Primary Testing Method: The Web Dashboard**

The most effective way to test and verify the project is by using the interactive web application. It provides a visual and intuitive way to confirm that all components are working correctly and to see the final, impressive results.

### **Step 1: Environment Verification**

Before launching, run the system check script to ensure your environment is correctly configured:

```bash
python check_system.py
```

**Expected Output:** The script will confirm your Python version and that all required packages (Flask, NumPy, etc.) are installed.

### **Step 2: Launch and Explore the Web Application**

1.  **Launch the server**:
    ```bash
    python start_webapp.py
    ```
2.  **Open your browser** and navigate to **`http://localhost:5000`**.

3.  **Verification Checklist**:
    - ✅ **Dashboard (`/`)**: Does the main dashboard load without errors? Do you see the high-level KPI cards?
    - ✅ **Host Management (`/hosts`)**: Does the page load? Do you see a grid of host cards with utilization bars and a status badge for each?
    - ✅ **Comparison Analysis (`/comparison`)**: This is the most important page to verify. Does it load correctly? Do you see:
        - The main data table with the `Hybrid-AI` listed as the top performer?
        - The **Algorithm Scorecards** section with a radar chart for each algorithm?
        - The **Cost vs. Efficiency Frontier** scatter plot?
        - Detailed takeaways for each section?
    - ✅ **Other Pages**: Briefly click on the "Tenants", "Audit", and "Placement" links in the sidebar to ensure they load without errors.

If you can successfully check all these boxes, the application is working as intended.

---

## ⚙️ **Optional: Core Engine Sanity Check**

If you want to quickly test the underlying Python simulation engine without the UI, you can run the simple test script.

```bash
python src/simple_enhanced_test.py
```

**Expected Output:** This will run a very small-scale simulation and use `matplotlib` to display a basic comparison chart. It's a quick way to confirm the core Python logic is functional.

---

## 🔬 **Advanced Testing (For Developers)**

These steps are for users who want to dive deeper into the AI model itself.

- **AI Debugging**: To see a detailed, step-by-step breakdown of the `Hybrid-AI`'s decision-making process for a single VM placement, run:
  ```bash
  python debug_ai_placement.py
  ```

- **Re-training the AI Model**: To run the full AI model training pipeline from scratch, you can execute the trainer script. **Note:** This is computationally intensive and can take several minutes.
  ```bash
  python src/advanced_model_trainer.py
  ```
  This will regenerate the `hybrid_ai_predictor.pkl` file in the `models/` directory.
