#!/usr/bin/env python3
"""
Enterprise VM Placement Web Application Launcher
Launch the web interface for the Enhanced VM Placement Simulation System
"""

import os
import sys
import webbrowser
import threading
import time

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')
    print("\n🌐 Browser opened at: http://localhost:5000")

def main():
    print("""
    🚀 Enhanced VM Placement Simulation System
    ==========================================
    
    🏢 Enterprise-Grade VM Placement Web Interface
    
    Features included:
    ✅ Interactive Dashboard with Real-time Metrics
    ✅ VM Placement Request Interface
    ✅ Multi-Tenant Management System
    ✅ Comprehensive Audit & Compliance Dashboard
    ✅ Advanced Analytics & Reports
    ✅ Enterprise-Ready Design with Bootstrap 5
    ✅ Real-time Charts and Visualizations
    
    🎯 Key Capabilities:
    • Multi-tenant support with compliance frameworks
    • AI-enhanced placement algorithms
    • Real-time performance monitoring
    • Executive dashboards and reporting
    • Audit trails and compliance tracking
    
    Starting web server...
    """)
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Import and run the Flask app
    try:
        from app import app
        print("✅ Flask application loaded successfully")
        print("🌐 Web interface available at: http://localhost:5000")
        print("\n" + "="*50)
        print("📊 Available Pages:")
        print("   • Dashboard:     http://localhost:5000/")
        print("   • VM Placement:  http://localhost:5000/placement")
        print("   • Tenants:       http://localhost:5000/tenants")
        print("   • Audit:         http://localhost:5000/audit")
        print("   • Reports:       http://localhost:5000/reports")
        print("="*50)
        print("\n⚠️  Press Ctrl+C to stop the server\n")
        
        # Run the Flask application
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
        
    except ImportError as e:
        print(f"❌ Error importing Flask application: {e}")
        print("\n💡 Make sure all required packages are installed:")
        print("   pip install Flask numpy matplotlib seaborn")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Web server stopped.")
        print("Thank you for using the Enhanced VM Placement System!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting web application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()