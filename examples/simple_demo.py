#!/usr/bin/env python3
"""Simple demonstration of GPS spoofing detection with guaranteed visible graph."""

import matplotlib
matplotlib.use('TkAgg')  # Force Tk backend
import matplotlib.pyplot as plt
import numpy as np
import time

from gps_modulator.visualization import LivePathPlotter

def simple_demo():
    """Simple demo that ensures the graph is visible."""
    print("GPS Spoofing Detection Demo")
    print("=" * 40)
    
    # Create plotter with visible settings
    plotter = LivePathPlotter(max_points=100, title="GPS Spoofing Detection - Live Demo")
    plotter.setup_plot()
    
    # Create sample GPS path around San Francisco
    base_lat, base_lon = 37.7749, -122.4194
    
    print("Generating sample GPS data...")
    
    # Generate a simple path with some spoofing events
    for i in range(30):
        # Normal movement
        lat = base_lat + (i * 0.0001)
        lon = base_lon + (i * 0.0001)
        
        # Add spoofing every 5th point
        is_spoofed = (i % 5 == 0)
        if is_spoofed:
            lat += 0.001  # Sudden jump for spoofing
            lon += 0.001
        
        point = {'latitude': lat, 'longitude': lon}
        
        plotter.add_point(
            raw_point=point,
            corrected_point=point,
            is_spoofed=is_spoofed
        )
        
        # Update plot
        plotter.update_plot(None)
        
        if i == 0:
            print("Graph window should now be visible!")
            print("Blue line: GPS path")
            print("Red dots: Detected spoofing")
            print("\nThe graph shows:")
            print("   - Normal GPS movement (gradual changes)")
            print("   - Spoofing events (sudden jumps marked in red)")
        
        time.sleep(0.5)
    
    # Ensure window stays open
    print("\nDemo complete! Graph is now visible.")
    print("   Close the matplotlib window to exit.")
    
    try:
        # Force window to stay open
        plt.ioff()  # Turn off interactive mode
        plt.show(block=True)  # Block until window closed
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Fallback: save to file if display fails
        plt.savefig('gps_demo_output.png')
        print("Graph saved to gps_demo_output.png")
    finally:
        plotter.close()

if __name__ == "__main__":
    simple_demo()