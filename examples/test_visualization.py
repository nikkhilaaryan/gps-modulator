#!/usr/bin/env python3
"""Simple test script to verify visualization is working."""

import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import os

# Add the source directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gps_spoofing_detector.visualization import LivePathPlotter

def test_visualization():
    """Test the live visualization with sample data."""
    print("Testing GPS spoofing detection visualization...")
    
    # Create plotter
    plotter = LivePathPlotter(max_points=50, title="GPS Spoofing Detection Test")
    plotter.setup_plot()
    
    # Add some initial sample data to make the graph visible
    sample_points = [
        {'latitude': 37.7749, 'longitude': -122.4194},
        {'latitude': 37.7750, 'longitude': -122.4195},
        {'latitude': 37.7751, 'longitude': -122.4196},
        {'latitude': 37.7752, 'longitude': -122.4197},
        {'latitude': 37.7753, 'longitude': -122.4198},
    ]
    
    # Add sample points to make graph visible
    for i, point in enumerate(sample_points):
        plotter.add_point(
            raw_point=point,
            corrected_point=point,
            is_spoofed=(i % 3 == 0)  # Mark some as spoofed
        )
    
    # Start animation
    print("Starting animation...")
    plotter.start_animation(interval=1000)
    
    # Keep the window open
    try:
        print("Graph window should be visible now. Press Ctrl+C to close.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClosing visualization...")
    finally:
        plotter.close()

if __name__ == "__main__":
    test_visualization()