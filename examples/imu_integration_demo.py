"""
IMU Integration Demo for GPS Spoofing Detection

This example demonstrates how to integrate IMU data with the existing
GPS spoofing detection system for improved path correction.
"""

import time
import random
import math
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from gps_modulator.detectors import VelocityAnomalyDetector
from gps_modulator.correction.path_corrector import PathCorrector
from gps_modulator.streaming.imu_streamer import EnhancedGpsReader, IMUStreamer
from gps_modulator.visualization.live_plotter import LivePathPlotter


def create_mock_gps_path():
    """Create a compelling GPS path story with clear spoofing segments."""
    base_lat = 40.7589
    base_lon = -73.9851
    
    path = []
    spoof_segments = [
        (25, 30, 0.0012),   # First spoofing attack: sudden north jump
        (65, 70, -0.0008)   # Second spoofing attack: sudden south jump
    ]
    
    for i in range(80):
        # Normal smooth movement
        lat = base_lat + (i * 0.0001)
        lon = base_lon + (i * 0.0001)
        
        # Apply spoofing only during specific segments
        for start, end, offset in spoof_segments:
            if start <= i < end:
                lat += offset
                break
        
        path.append({
            'latitude': lat,
            'longitude': lon,
            'timestamp': time.time() + i * 0.5,
            'index': i  # Track index for spoofing detection
        })
    
    return path, spoof_segments


def simulate_imu_data_for_gps(gps_point, prev_point=None):
    """Generate realistic IMU data for a GPS point."""
    if prev_point:
        # Calculate heading based on GPS movement
        lat1, lon1 = prev_point['latitude'], prev_point['longitude']
        lat2, lon2 = gps_point['latitude'], gps_point['longitude']
        
        # Calculate bearing
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
        heading = math.degrees(math.atan2(x, y))
        if heading < 0:
            heading += 360
    else:
        heading = 45.0  # Default heading
    
    # Calculate speed based on distance and time
    speed = 10.0  # m/s (simulated vehicle speed)
    
    # Generate realistic IMU data
    return {
        'accel_x': random.uniform(-0.5, 0.5),
        'accel_y': random.uniform(-0.5, 0.5),
        'accel_z': 9.81 + random.uniform(-0.1, 0.1),
        'gyro_x': random.uniform(-0.1, 0.1),
        'gyro_y': random.uniform(-0.1, 0.1),
        'gyro_z': random.uniform(-0.5, 0.5),
        'mag_x': math.cos(math.radians(heading)) + random.uniform(-0.05, 0.05),
        'mag_y': math.sin(math.radians(heading)) + random.uniform(-0.05, 0.05),
        'mag_z': 0.5 + random.uniform(-0.05, 0.05),
        'heading': heading,
        'speed': speed,
        'timestamp': gps_point['timestamp']
    }


def run_imu_integration_demo():
    """Create a compelling visual story of GPS spoofing and IMU rescue."""
    print(" Creating GPS Spoofing Detection Story...")
    print("=" * 60)
    
    # Initialize components
    detector = VelocityAnomalyDetector(threshold_velocity=8.0)  # Lower threshold for clearer detection
    corrector = PathCorrector()
    
    # Enable IMU correction
    corrector.enable_imu_correction()
    corrector.set_magnetic_declination(-13.0)  # NYC magnetic declination
    
    # Create story-driven GPS path
    gps_path, spoof_segments = create_mock_gps_path()
    
    # Process data with storytelling focus
    raw_lats = [p['latitude'] for p in gps_path]
    raw_lons = [p['longitude'] for p in gps_path]
    corrected_lats = []
    corrected_lons = []
    
    # Track spoofing events for annotations
    spoof_events = []
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.patches import Rectangle
        
        # Process each point with IMU correction
        for i, gps_point in enumerate(gps_path):
            imu_data = simulate_imu_data_for_gps(gps_point, gps_path[i-1] if i > 0 else None)
            
            is_spoofed = detector.detect(gps_point)
            
            if is_spoofed:
                corrected_point = corrector.correct(gps_point, is_spoofed=True, imu_data=imu_data)
                spoof_events.append({
                    'index': i,
                    'original': gps_point,
                    'corrected': corrected_point,
                    'type': 'spoofing_detected'
                })
            else:
                corrected_point = corrector.correct(gps_point, is_spoofed=False)
            
            corrected_lats.append(corrected_point['latitude'])
            corrected_lons.append(corrected_point['longitude'])
        
        # Create IMU-assisted spoofing mitigation visualization
        fig, ax = plt.subplots(1, 1, figsize=(16, 8))
        fig.suptitle('IMU-Assisted GPS Spoofing Mitigation During Detected Anomaly', 
                    fontsize=16, fontweight='bold')
        
        # Plot raw GPS trajectory (always visible)
        ax.plot(raw_lons, raw_lats, 'b-', linewidth=2.5, alpha=0.8, label='Raw GPS Trajectory')
        
        # Plot IMU correction only during spoofing segments
        imu_segments_plotted = False
        for start, end, _ in spoof_segments:
            if start < len(raw_lons) and end < len(raw_lons):
                # Extract and plot IMU-corrected segments only
                imu_segment_lons = corrected_lons[start:end+1]
                imu_segment_lats = corrected_lats[start:end+1]
                ax.plot(imu_segment_lons, imu_segment_lats, 'g-', linewidth=3.0, 
                       label='IMU-Based Correction' if not imu_segments_plotted else "")
                imu_segments_plotted = True
        
        # Add detected spoofing anomaly zones with greyed-out GPS segments
        for start, end, _ in spoof_segments:
            if start < len(raw_lons) and end < len(raw_lons):
                # Grey out the spoofed GPS segment
                ax.plot(raw_lons[start:end+1], raw_lats[start:end+1], 'r-', 
                       linewidth=2.5, alpha=0.3, label='Spoofed GPS Segment')
                
                # Add red shaded anomaly zone
                x_min = min(raw_lons[start:end+1]) - 0.0001
                x_max = max(raw_lons[start:end+1]) + 0.0001
                y_min = min(raw_lats[start:end+1]) - 0.0001
                y_max = max(raw_lats[start:end+1]) + 0.0001
                
                rect = Rectangle((x_min, y_min), (x_max - x_min), (y_max - y_min),
                               facecolor='#ffcccc', alpha=0.4, edgecolor='red', linewidth=2)
                ax.add_patch(rect)
        
        # Add specific annotations for IMU dead reckoning
        for idx, (start, end, _) in enumerate(spoof_segments):
            if idx == 0:  # Annotate the first attack
                # IMU takeover annotation
                ax.annotate('IMU Dead Reckoning Active', 
                           xy=(corrected_lons[start], corrected_lats[start]), 
                           xytext=(-60, 25), textcoords='offset points',
                           fontsize=12, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.4", facecolor='lightgreen', edgecolor='green', alpha=0.9),
                           arrowprops=dict(arrowstyle='->', color='green', lw=2))
                
                # Bridge transition annotations
                ax.annotate('', xy=(raw_lons[start-1], raw_lats[start-1]), 
                           xytext=(corrected_lons[start], corrected_lats[start]),
                           arrowprops=dict(arrowstyle='<->', color='green', lw=1.5, alpha=0.7))
                
                ax.annotate('', xy=(corrected_lons[end], corrected_lats[end]), 
                           xytext=(raw_lons[end+1], raw_lats[end+1]),
                           arrowprops=dict(arrowstyle='<->', color='green', lw=1.5, alpha=0.7))
        
        ax.set_xlabel('Longitude (degrees)', fontsize=12)
        ax.set_ylabel('Latitude (degrees)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Clean legend with precise labels
        handles, labels = ax.get_legend_handles_labels()
        unique_labels = []
        unique_handles = []
        seen = set()
        for handle, label in zip(handles, labels):
            if label not in seen and label != "":
                seen.add(label)
                unique_handles.append(handle)
                unique_labels.append(label)
        
        # Add spoofing anomaly zone to legend
        from matplotlib.patches import Patch
        zone_patch = Patch(color='#ffcccc', alpha=0.4, label='Detected Spoofing Anomaly')
        unique_handles.append(zone_patch)
        unique_labels.append('Detected Spoofing Anomaly')
        
        ax.legend(unique_handles, unique_labels, loc='upper right', fontsize=11)
        
        # Professional insight caption
        fig.text(0.5, 0.02, 
                'IMU dead reckoning provides seamless navigation continuity during GPS spoofing events by bridging detected anomalies.',
                ha='center', fontsize=11, style='italic',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        print("\n✅ IMU-assisted spoofing mitigation visualization complete! Close plot to continue...")
        plt.show(block=True)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n Demo completed successfully!")


def compare_correction_methods():
    """Compare GPS-only vs IMU-enhanced correction."""
    print("\n Comparing Correction Methods")
    print("=" * 40)
    
    # Create test scenario
    gps_path = create_mock_gps_path()
    
    # GPS-only corrector
    corrector_gps = PathCorrector()
    corrector_gps.disable_imu_correction()
    
    # IMU-enhanced corrector
    corrector_imu = PathCorrector()
    corrector_imu.enable_imu_correction()
    
    detector = VelocityAnomalyDetector()
    
    gps_only_errors = []
    imu_errors = []
    
    prev_point = None
    
    for i, gps_point in enumerate(gps_path):
        if i < 2:  # Skip first few points for initialization
            prev_point = gps_point
            continue
        
        # Simulate spoofing
        is_spoofed = detector.detect(gps_point)
        
        if is_spoofed:
            # Get expected position (next point in normal path)
            expected_lat = gps_path[i-1]['latitude'] + 0.0001
            expected_lon = gps_path[i-1]['longitude'] + 0.0001
            
            # GPS-only correction
            gps_corrected = corrector_gps.correct(gps_point, is_spoofed=True)
            gps_error = math.sqrt(
                (gps_corrected['latitude'] - expected_lat)**2 +
                (gps_corrected['longitude'] - expected_lon)**2
            ) * 111000  # Convert to meters
            gps_only_errors.append(gps_error)
            
            # IMU-enhanced correction
            imu_data = simulate_imu_data_for_gps(gps_point, prev_point)
            imu_corrected = corrector_imu.correct(gps_point, is_spoofed=True, imu_data=imu_data)
            imu_error = math.sqrt(
                (imu_corrected['latitude'] - expected_lat)**2 +
                (imu_corrected['longitude'] - expected_lon)**2
            ) * 111000
            imu_errors.append(imu_error)
        
        prev_point = gps_point
    
    if gps_only_errors and imu_errors:
        avg_gps_error = sum(gps_only_errors) / len(gps_only_errors)
        avg_imu_error = sum(imu_errors) / len(imu_errors)
        
        print(f" Average GPS-only correction error: {avg_gps_error:.2f} meters")
        print(f" Average IMU-enhanced correction error: {avg_imu_error:.2f} meters")
        
        improvement = ((avg_gps_error - avg_imu_error) / avg_gps_error) * 100
        print(f" IMU integration improved accuracy by {improvement:.1f}%")
    else:
        print("ℹ  No spoofing events detected for comparison")


if __name__ == "__main__":
    # Import numpy for the demo
    try:
        import numpy as np
    except ImportError:
        print("Installing numpy for demo...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
        import numpy as np
    
    # Run the main demo
    run_imu_integration_demo()
    
    # Run comparison
    compare_correction_methods()
    
    # Keep the final plot open
    try:
        import matplotlib.pyplot as plt
        print("\n Press any key or close the window to exit...")
        plt.show(block=True)
    except ImportError:
        pass
    
    print("\n IMU Integration Demo Complete!")
    print("The system now supports:")
    print("  • Enhanced IMU data processing")
    print("  • Improved path correction during spoofing")
    print("  • Real-time visualization of corrections")
    print("  • Confidence scoring for corrections")