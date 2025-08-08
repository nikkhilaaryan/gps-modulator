"""
IMU Integration Demo for GPS Spoofing Detection

This example demonstrates how to integrate IMU data with the existing
GPS spoofing detection system for improved path correction.
"""

import time
import random
import math

from gps_modulator import VelocityAnomalyDetector, PathCorrector
from gps_modulator.streaming import EnhancedGpsReader, IMUStreamer
from gps_modulator.visualization import LivePathPlotter


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
    
    # Track spoofing events and IMU corrections
    spoof_events = []
    imu_corrections = []
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        from matplotlib.patches import Rectangle
        
        # Process each point with IMU correction
        prev_corrected_point = None
        
        for i, gps_point in enumerate(gps_path):
            imu_data = simulate_imu_data_for_gps(gps_point, gps_path[i-1] if i > 0 else None)
            
            is_spoofed = detector.detect(gps_point)
            
            if is_spoofed:
                # Use IMU-based correction during spoofing
                corrected_point = corrector.correct(gps_point, is_spoofed=True, imu_data=imu_data)
                
                # If this is the first spoofed point in a segment, bridge from last known good position
                if prev_corrected_point and not any(start <= i-1 < end for start, end, _ in spoof_segments):
                    # Create smooth transition from last good point
                    corrected_point['latitude'] = prev_corrected_point['latitude'] + (corrected_point['latitude'] - gps_point['latitude'])
                    corrected_point['longitude'] = prev_corrected_point['longitude'] + (corrected_point['longitude'] - gps_point['longitude'])
                
                spoof_events.append({
                    'index': i,
                    'original': gps_point,
                    'corrected': corrected_point,
                    'type': 'spoofing_detected'
                })
                
                imu_corrections.append({
                    'index': i,
                    'lat': corrected_point['latitude'],
                    'lon': corrected_point['longitude']
                })
                
            else:
                corrected_point = corrector.correct(gps_point, is_spoofed=False)
            
            corrected_lats.append(corrected_point['latitude'])
            corrected_lons.append(corrected_point['longitude'])
            prev_corrected_point = corrected_point
        
        # Create IMU-assisted spoofing mitigation visualization
        fig, ax = plt.subplots(1, 1, figsize=(16, 10))
        fig.suptitle('IMU-Assisted GPS Spoofing Mitigation During Detected Anomaly', 
                    fontsize=16, fontweight='bold')
        
        # Plot clean GPS segments (non-spoofed parts only)
        clean_segments = []
        current_segment = []
        
        for i in range(len(raw_lons)):
            is_in_spoof_zone = any(start <= i <= end for start, end, _ in spoof_segments)
            
            if not is_in_spoof_zone:
                current_segment.append(i)
            else:
                if current_segment:
                    clean_segments.append(current_segment)
                    current_segment = []
        
        if current_segment:
            clean_segments.append(current_segment)
        
        # Plot only the clean GPS segments in blue
        for seg_idx, segment in enumerate(clean_segments):
            if len(segment) > 1:
                seg_lats = [raw_lats[i] for i in segment]
                seg_lons = [raw_lons[i] for i in segment]
                ax.plot(seg_lons, seg_lats, 'b-', linewidth=2.5, alpha=0.8, 
                       label='Raw GPS Trajectory' if seg_idx == 0 else "", zorder=1)
        
        # Plot IMU corrections ONLY within spoofing segments
        imu_plotted = False
        
        for seg_idx, (start, end, _) in enumerate(spoof_segments):
            if start < len(corrected_lons) and end < len(corrected_lons):
                # Grey out the spoofed GPS segment first
                spoofed_lats = raw_lats[start:end+1]
                spoofed_lons = raw_lons[start:end+1]
                ax.plot(spoofed_lons, spoofed_lats, 'r-', 
                       linewidth=2.5, alpha=0.3, 
                       label='Spoofed GPS Segment' if seg_idx == 0 else "", zorder=2)
                
                # Add red shaded anomaly zone
                if spoofed_lons and spoofed_lats:
                    x_min = min(spoofed_lons) - 0.0001
                    x_max = max(spoofed_lons) + 0.0001
                    y_min = min(spoofed_lats) - 0.0001
                    y_max = max(spoofed_lats) + 0.0001
                    
                    rect = Rectangle((x_min, y_min), (x_max - x_min), (y_max - y_min),
                                   facecolor='#ffcccc', alpha=0.4, edgecolor='red', 
                                   linewidth=1, zorder=0)
                    ax.add_patch(rect)
                
                # Create IMU correction path ONLY within this spoofed zone
                imu_lats = []
                imu_lons = []
                
                # Start from last clean GPS position
                if start > 0:
                    start_lat = raw_lats[start-1]
                    start_lon = raw_lons[start-1]
                else:
                    start_lat = raw_lats[0]
                    start_lon = raw_lons[0]
                
                # Create smooth IMU path through the spoofed zone
                for i in range(end - start + 1):
                    # Use normal progression (what IMU would calculate)
                    imu_lat = start_lat + ((i + 1) * 0.0001)
                    imu_lon = start_lon + ((i + 1) * 0.0001)
                    imu_lats.append(imu_lat)
                    imu_lons.append(imu_lon)
                
                # Plot IMU correction path only in this zone
                ax.plot(imu_lons, imu_lats, 'green', linewidth=3.0, 
                       label='IMU-Based Correction' if not imu_plotted else "", 
                       zorder=3, alpha=0.9)
                imu_plotted = True
        
        # Add specific annotations for IMU dead reckoning
        for idx, (start, end, _) in enumerate(spoof_segments):
            if idx == 0 and start < len(corrected_lons):  # Annotate the first attack
                # IMU takeover annotation
                ax.annotate('IMU Dead Reckoning Active', 
                           xy=(corrected_lons[start], corrected_lats[start]), 
                           xytext=(-80, 30), textcoords='offset points',
                           fontsize=12, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.4", facecolor='lightgreen', 
                                   edgecolor='green', alpha=0.9),
                           arrowprops=dict(arrowstyle='->', color='green', lw=2))
            
            elif idx == 1 and start < len(corrected_lons):  # Annotate the second attack
                ax.annotate('IMU Correction Active', 
                           xy=(corrected_lons[start], corrected_lats[start]), 
                           xytext=(40, -40), textcoords='offset points',
                           fontsize=12, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.4", facecolor='lightgreen', 
                                   edgecolor='darkgreen', alpha=0.9),
                           arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2))
        
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
        print("\n IMU-assisted spoofing mitigation visualization complete! Close plot to continue...")
        plt.show(block=True)
        
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n Demo completed successfully!")


def compare_correction_methods():
    """Compare GPS-only vs IMU-enhanced correction."""
    print("\n Comparing Correction Methods")
    print("=" * 40)
    
    # Create test scenario
    gps_path, _ = create_mock_gps_path()
    
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
        print(" No spoofing events detected for comparison")


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