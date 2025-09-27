"""
System Prerequisites Check for Enhanced VM Placement System
"""

import sys
import os
import importlib.util

def check_python_version():
    """Check Python version"""
    print("🐍 PYTHON VERSION CHECK")
    print("-" * 30)
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_required_packages():
    """Check if required packages are installed"""
    print("\n📦 PACKAGE REQUIREMENTS CHECK")
    print("-" * 30)
    
    required_packages = [
        'numpy', 'pandas', 'matplotlib', 'scikit-learn', 
        'joblib', 'seaborn', 'xgboost'
    ]
    
    missing_packages = []
    installed_packages = []
    
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is not None:
                # Try to import to verify it works
                module = importlib.import_module(package)
                if hasattr(module, '__version__'):
                    version = module.__version__
                else:
                    version = "unknown"
                print(f"✅ {package:15} - v{version}")
                installed_packages.append(package)
            else:
                print(f"❌ {package:15} - NOT INSTALLED")
                missing_packages.append(package)
        except ImportError as e:
            print(f"❌ {package:15} - IMPORT ERROR: {e}")
            missing_packages.append(package)
    
    return missing_packages, installed_packages

def check_directory_structure():
    """Check if required directories exist"""
    print("\n📁 DIRECTORY STRUCTURE CHECK")
    print("-" * 30)
    
    required_dirs = ['src', 'data', 'results']
    missing_dirs = []
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            missing_dirs.append(dir_name)
    
    return missing_dirs

def check_source_files():
    """Check if required source files exist"""
    print("\n📄 SOURCE FILES CHECK")
    print("-" * 30)
    
    required_files = [
        'src/enhanced_simulator.py',
        'src/enhanced_algorithms.py', 
        'src/advanced_model_trainer.py',
        'src/data_generator.py',
        'src/simple_enhanced_test.py',
        'src/final_demonstration.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path:30} ({size:,} bytes)")
        else:
            print(f"❌ {file_path:30} MISSING")
            missing_files.append(file_path)
    
    return missing_files

def check_memory_and_disk():
    """Check system resources"""
    print("\n💻 SYSTEM RESOURCES CHECK")
    print("-" * 30)
    
    try:
        import psutil
        
        # Memory check
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"Total RAM: {memory_gb:.1f} GB")
        
        if memory_gb >= 4:
            print("✅ Sufficient RAM for basic testing")
        elif memory_gb >= 2:
            print("⚠️  Limited RAM - reduce dataset sizes for large tests")
        else:
            print("❌ Insufficient RAM - may have issues with large datasets")
        
        # Disk space check
        disk = psutil.disk_usage('.')
        disk_gb_free = disk.free / (1024**3)
        print(f"Free Disk Space: {disk_gb_free:.1f} GB")
        
        if disk_gb_free >= 1:
            print("✅ Sufficient disk space")
        else:
            print("❌ Low disk space - may have issues saving results")
            
    except ImportError:
        print("⚠️  psutil not available - cannot check system resources")
        print("Install with: pip install psutil")

def generate_install_commands(missing_packages):
    """Generate installation commands for missing packages"""
    if missing_packages:
        print(f"\n🔧 INSTALLATION COMMANDS")
        print("-" * 30)
        print("To install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        print("\nOr install all at once:")
        all_packages = ['numpy', 'pandas', 'matplotlib', 'scikit-learn', 'joblib', 'seaborn', 'xgboost', 'psutil']
        print(f"pip install {' '.join(all_packages)}")

def create_missing_directories(missing_dirs):
    """Create missing directories"""
    if missing_dirs:
        print(f"\n📁 CREATING MISSING DIRECTORIES")
        print("-" * 30)
        for dir_name in missing_dirs:
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ Created {dir_name}/ directory")
            except Exception as e:
                print(f"❌ Failed to create {dir_name}/: {e}")

def main():
    """Main system check function"""
    print("🚀 Enhanced VM Placement System - Prerequisites Check")
    print("=" * 60)
    
    # Check Python version
    python_ok = check_python_version()
    
    # Check packages
    missing_packages, installed_packages = check_required_packages()
    
    # Check directories
    missing_dirs = check_directory_structure()
    
    # Check source files
    missing_files = check_source_files()
    
    # Check system resources
    check_memory_and_disk()
    
    # Summary
    print(f"\n🎯 SYSTEM READINESS SUMMARY")
    print("=" * 60)
    
    issues = 0
    
    if not python_ok:
        print("❌ Python version compatibility issue")
        issues += 1
    
    if missing_packages:
        print(f"❌ {len(missing_packages)} missing packages: {', '.join(missing_packages)}")
        issues += 1
        generate_install_commands(missing_packages)
    
    if missing_dirs:
        print(f"❌ {len(missing_dirs)} missing directories: {', '.join(missing_dirs)}")
        create_missing_directories(missing_dirs)
        issues += 1
    
    if missing_files:
        print(f"❌ {len(missing_files)} missing source files")
        issues += 1
    
    if issues == 0:
        print("🎉 SYSTEM IS READY!")
        print("✅ All prerequisites satisfied")
        print("\nNext steps:")
        print("1. python src/simple_enhanced_test.py           # Basic test (2 min)")
        print("2. python src/final_demonstration.py           # Full demo (5 min)")
        print("3. python src/data_generator.py                # Generate data (1 min)")
    else:
        print(f"⚠️  SYSTEM HAS {issues} ISSUES")
        print("Please resolve the issues above before testing")
        
        if missing_packages:
            print(f"\n🔧 Quick fix for packages:")
            print(f"pip install {' '.join(missing_packages)}")
    
    print(f"\n📋 Installation Status:")
    print(f"✅ Installed packages: {len(installed_packages)}")
    print(f"❌ Missing packages: {len(missing_packages)}")
    print(f"📁 Ready directories: {3 - len(missing_dirs)}/3")
    print(f"📄 Available files: {6 - len(missing_files)}/6")

if __name__ == "__main__":
    main()