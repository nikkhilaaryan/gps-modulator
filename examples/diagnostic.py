#!/usr/bin/env python3
"""
Diagnostic script to troubleshoot matplotlib display issues on Windows.
"""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import platform

def run_diagnostics():
    """Run comprehensive diagnostics for matplotlib display issues."""
    
    print("🩺 MATLABPLOT DIAGNOSTIC REPORT")
    print("=" * 50)
    
    # System information
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Python Version: {sys.version}")
    print(f"Matplotlib Version: {matplotlib.__version__}")
    print(f"Current Backend: {matplotlib.get_backend()}")
    
    # Available backends
    print("\n AVAILABLE BACKENDS:")
    backends = matplotlib.rcsetup.interactive_bk
    for i, backend in enumerate(backends, 1):
        print(f"   {i}. {backend}")
    
    # Test simple plot
    print("\n TESTING SIMPLE PLOT...")
    try:
        # Create a simple test plot
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Create test data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        
        ax.plot(x, y, 'b-', linewidth=2, label='Test Sine Wave')
        ax.set_title('Diagnostic Test Plot', fontsize=14, fontweight='bold')
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        print(" Plot created successfully")
        
        # Try to display
        print(" ATTEMPTING TO DISPLAY...")
        
        # Force window to front (Windows-specific)
        if platform.system() == 'Windows':
            try:
                fig_manager = plt.get_current_fig_manager()
                fig_manager.window.state('zoomed')
                fig_manager.window.lift()
                fig_manager.window.attributes('-topmost', True)
                fig_manager.window.attributes('-topmost', False)
                print(" Window management applied")
            except Exception as e:
                print(f" Window management failed: {e}")
        
        # Show plot
        plt.show(block=True)
        print(" Plot displayed successfully!")
        
    except Exception as e:
        print(f" ERROR: {e}")
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("1. Ensure you have a display (not running headless)")
        print("2. Try running: python -m pip install --upgrade matplotlib")
        print("3. Try different backend: matplotlib.use('Qt5Agg')")
        print("4. Check if antivirus is blocking matplotlib")
        print("5. Run as administrator if needed")
        
        # Test non-interactive backend
        print("\n Testing non-interactive backend...")
        try:
            matplotlib.use('Agg')
            fig, ax = plt.subplots()
            ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
            plt.savefig('test_plot.png')
            print(" Non-interactive plot saved as 'test_plot.png'")
            print("   Check current directory for the saved plot")
        except Exception as e2:
            print(f" Non-interactive also failed: {e2}")

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n DEPENDENCY CHECK:")
    
    required_packages = ['matplotlib', 'numpy']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f" {package} is installed")
        except ImportError:
            print(f" {package} is NOT installed")
            print(f"   Install with: pip install {package}")

def check_display():
    """Check display environment."""
    print("\n  DISPLAY ENVIRONMENT:")
    
    # Check for display environment variables
    display_vars = ['DISPLAY', 'WAYLAND_DISPLAY', 'MPLBACKEND']
    for var in display_vars:
        value = os.environ.get(var)
        if value:
            print(f"   {var}: {value}")
        else:
            print(f"   {var}: Not set")
    
    # Check if running in WSL
    if 'WSL_DISTRO_NAME' in os.environ:
        print("   Running in WSL - may need X11 server")
        print("   Install: sudo apt install x11-apps")
        print("   Run: export DISPLAY=:0")

if __name__ == "__main__":
    check_dependencies()
    check_display()
    run_diagnostics()