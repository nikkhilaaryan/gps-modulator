# import pytest
import matplotlib
matplotlib.use('TkAgg') 

import matplotlib.pyplot as plt
from gps_modulator.detectors.velocity_anomaly import velocity_anomaly_detector
from gps_modulator.fallback.fallback_manager import FallbackManager
from visualize.path_plotter import plot_paths


def test_pipeline_visual():
    # Sample GPS + IMU data stream
    gps_points = [
        {'lat': 19.0760, 'lon': 72.8777, 'timestamp': 0},
        {'lat': 19.0761, 'lon': 72.8780, 'timestamp': 5},
        {'lat': 19.0800, 'lon': 72.8800, 'timestamp': 10},  # spoofed
        {'lat': 19.0801, 'lon': 72.8802, 'timestamp': 15}
    ]

    imu_data = [
        {'acceleration': 0.3, 'heading': 90.0, 'velocity': 5.0},
        {'acceleration': 0.2, 'heading': 90.0, 'velocity': 5.3},
        {'acceleration': 0.1, 'heading': 90.0, 'velocity': 10.0},  # spoofed
        {'acceleration': 0.0, 'heading': 90.0, 'velocity': 10.0}
    ]

    # Components
    velocity_detector = velocity_anomaly_detector(threshold_velocity=30.0)
    fallback_manager = FallbackManager()

    # Result buffers
    spoof_flags = []
    fallback_path = []

    for i in range(len(gps_points)):
        current = gps_points[i]
        spoofed = velocity_detector.detect(current)
        spoof_flags.append(spoofed)

        if spoofed:
            if i > 0:
                dt = current['timestamp'] - gps_points[i-1]['timestamp']
            else:
                dt = 1.0
            fallback_pos = fallback_manager.handle_fallback(gps_points[i-1], imu_data[i], dt)
            fallback_path.append(fallback_pos)
        else:
            fallback_path.append(None)

    # Plot the paths (comment out if not needed in test)
    plot_paths(gps_points, fallback_path, spoof_flags)

    # Assertions
    # assert spoof_flags == [False, False, True, False], "Spoof detection flags do not match expected"
    # assert len(fallback_path) == 4
    # assert fallback_path[2] is not None, "Fallback position should be computed for spoofed point"

if __name__ == "__main__":
    test_pipeline_visual()
