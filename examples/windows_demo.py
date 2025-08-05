#!/usr/bin/env python3
"""
Windows-specific demo for GPS spoofing detection visualization.
This version handles common Windows matplotlib display issues.
"""

import matplotlib
# Force specific backend for Windows
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import os

# Add the source directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gps_modulator.visualization.live_plotter import LivePathPlotter

def windows_demo():
    """Windows-specific demo with enhanced display handling."""
    print("Windows GPS Spoofing Detection Demo")
    print("=" * 50)
    
    # Check matplotlib backend
    print(f"Using matplotlib backend: {matplotlib.get_backend()}")
    
    # Create plotter with visible settings
    plotter = LivePathPlotter(max_points=50, title="GPS Spoofing Detection - Windows Demo")
    
    # Create sample data that will definitely show up
    print("Creating sample GPS path...")
    
    # Generate a clear, visible path
    base_lat, base_lon = 37.7749, -122.4194  # San Francisco coordinates
    
    # Create a simple square pattern that's easy to see
    coordinates = []
    for i in range(10):
        # Right
        coordinates.append({'lat': base_lat + i * 0.001, 'lon': base_lon})
    for i in range(10):
        # Up
        coordinates.append({'lat': base_lat + 0.009, 'lon': base_lon + i * 0.001})
    for i in range(10):
        # Left
        coordinates.append({'lat': base_lat + 0.009 - i * 0.001, 'lon': base_lon + 0.009})
    for i in range(10):
        # Down
        coordinates.append({'lat': base_lat, 'lon': base_lon + 0.009 - i * 0.001})
    
    # Add points to plotter
    for i, coord in enumerate(coordinates):
        point = {'latitude': coord['lat'], 'longitude': coord['lon']}
        is_spoofed = (i % 8 == 0)  # Mark every 8th point as spoofed
        
        plotter.add_point(
            raw_point=point,
            corrected_point=point,
            is_spoofed=is_spoofed
        )
        
        if i == 0:
            print("Setting up plot...")
            plotter.setup_plot()
            
            # Force window to front (Windows specific)
            try:
                fig_manager = plt.get_current_fig_manager()
                fig_manager.window.state('zoomed')
                fig_manager.window.lift()
                fig_manager.window.attributes('-topmost', True)
                fig_manager.window.attributes('-topmost', False)
                print("Window forced to front")
            except Exception as e:
                print(f"Could not force window to front: {e}")
    
    # Update plot with all data
    plotter.update_plot(None)
    
    print("\n" + "=" * 50)
    print(" GRAPH SHOULD BE VISIBLE NOW!")
    print("Look for a matplotlib window showing:")
    print("   - Blue square path (GPS track)")
    print("   - Red dots at corners (spoofing events)")
    print("   - Grid and legend")
    print("=" * 50)
    
    # Keep window open
    try:
        print("Press Ctrl+C or close the window to exit...")
        plt.ioff()  # Turn off interactive mode
        plt.show(block=True)  # Block until window closed
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Error displaying plot: {e}")
    finally:
        plotter.close()

if __name__ == "__main__":
    windows_demo()