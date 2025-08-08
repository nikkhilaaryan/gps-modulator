#!/usr/bin/env python3
"""Ultra-simple static demo that guarantees graph visibility."""

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

def static_demo():
    """Create a simple static plot that stays visible."""
    print("Creating guaranteed visible GPS spoofing demo...")
    
    # Create sample GPS data
    latitudes = [37.7749, 37.7750, 37.7751, 37.7752, 37.7753, 37.7763, 37.7764, 37.7765]
    longitudes = [-122.4194, -122.4195, -122.4196, -122.4197, -122.4198, -122.4208, -122.4209, -122.4210]
    
    # Mark spoofing events (sudden jumps)
    spoofed_indices = [5, 6]  # Points 5 and 6 show spoofing
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot the GPS path
    ax.plot(longitudes, latitudes, 'b-', linewidth=2, label='GPS Path')
    
    # Mark spoofed points
    spoofed_lats = [latitudes[i] for i in spoofed_indices]
    spoofed_lons = [longitudes[i] for i in spoofed_indices]
    ax.scatter(spoofed_lons, spoofed_lats, c='red', s=100, marker='o', 
               label='Detected Spoofing', zorder=5)
    
    # Mark normal points
    normal_indices = [i for i in range(len(latitudes)) if i not in spoofed_indices]
    normal_lats = [latitudes[i] for i in normal_indices]
    normal_lons = [longitudes[i] for i in normal_indices]
    ax.scatter(normal_lons, normal_lats, c='blue', s=50, alpha=0.7, label='Normal GPS')
    
    # Configure the plot
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.set_title('GPS Spoofing Detection Demo\n(Red dots indicate sudden position jumps)', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Set reasonable axis limits
    lat_padding = 0.001
    lon_padding = 0.001
    ax.set_xlim(min(longitudes) - lon_padding, max(longitudes) + lon_padding)
    ax.set_ylim(min(latitudes) - lat_padding, max(latitudes) + lat_padding)
    
    # Force window to front (Windows specific)
    try:
        fig_manager = plt.get_current_fig_manager()
        fig_manager.window.state('zoomed')
        fig_manager.window.lift()
        fig_manager.window.attributes('-topmost', True)
        fig_manager.window.attributes('-topmost', False)
        print("Window forced to front")
    except Exception as e:
        print(f"Note: Could not force window to front: {e}")
    
    print("\n" + "="*60)
    print(" GRAPH IS NOW VISIBLE!")
    print("You should see a matplotlib window showing:")
    print("   - Blue line: GPS path")
    print("   - Red dots: Detected spoofing events")
    print("   - Grid and legend")
    print("="*60)
    print("\nClose the matplotlib window to exit...")
    
    # Keep window open (blocking)
    try:
        plt.show(block=True)
    except KeyboardInterrupt:
        print("Demo interrupted")
    finally:
        plt.close()

if __name__ == "__main__":
    static_demo()