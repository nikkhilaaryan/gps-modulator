import pytest

# Handle matplotlib import gracefully for testing
try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for testing
    import matplotlib.pyplot as plt
    MPL_AVAILABLE = True
except ImportError:
    MPL_AVAILABLE = False
    plt = None
from gps_modulator.detectors.velocity_anomaly import VelocityAnomalyDetector
from gps_modulator.fallback.fallback_manager import FallbackManager
from visualize.path_plotter import plot_spoofing_scenario, create_demo_scenario


class TestPipelineVisual:
    """Comprehensive test suite for pipeline visualization."""
    
    def test_basic_pipeline(self):
        """Test basic pipeline functionality with simple GPS spoofing scenario."""
        if not MPL_AVAILABLE:
            pytest.skip("matplotlib not available")
            
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

        velocity_detector = VelocityAnomalyDetector(threshold_velocity=30.0)
        fallback_manager = FallbackManager()

        spoof_flags, fallback_path = self._run_pipeline(gps_points, imu_data, velocity_detector, fallback_manager)

        # Assertions
        assert len(spoof_flags) == 4
        assert len(fallback_path) == 4
        assert fallback_path[2] is not None, "Fallback position should be computed for spoofed point"

    def test_coordinate_format_compatibility(self):
        """Test pipeline with both coordinate formats (lat/lon and latitude/longitude)."""
        if not MPL_AVAILABLE:
            pytest.skip("matplotlib not available")
            
        gps_points_latlon = [
            {'lat': 19.0760, 'lon': 72.8777, 'timestamp': 0},
            {'latitude': 19.0761, 'longitude': 72.8780, 'timestamp': 5},
            {'lat': 19.0800, 'lon': 72.8800, 'timestamp': 10},
            {'latitude': 19.0801, 'longitude': 72.8802, 'timestamp': 15}
        ]

        imu_data = [
            {'acceleration': 0.3, 'heading': 90.0, 'velocity': 5.0},
            {'acceleration': 0.2, 'heading': 90.0, 'velocity': 5.3},
            {'acceleration': 0.1, 'heading': 90.0, 'velocity': 10.0},
            {'acceleration': 0.0, 'heading': 90.0, 'velocity': 10.0}
        ]

        velocity_detector = VelocityAnomalyDetector(threshold_velocity=30.0)
        fallback_manager = FallbackManager()

        spoof_flags, fallback_path = self._run_pipeline(gps_points_latlon, imu_data, velocity_detector, fallback_manager)

        assert len(spoof_flags) == 4
        assert len(fallback_path) == 4

    def test_multiple_spoofing_events(self):
        """Test pipeline with multiple spoofing events."""
        if not MPL_AVAILABLE:
            pytest.skip("matplotlib not available")
            
        gps_points = [
            {'lat': 19.0760, 'lon': 72.8777, 'timestamp': 0},
            {'lat': 19.0761, 'lon': 72.8780, 'timestamp': 5},
            {'lat': 19.0900, 'lon': 72.8850, 'timestamp': 10},  # spoofed
            {'lat': 19.0901, 'lon': 72.8851, 'timestamp': 15},  # spoofed
            {'lat': 19.0765, 'lon': 72.8785, 'timestamp': 20},  # normal
            {'lat': 19.0950, 'lon': 72.8900, 'timestamp': 25}   # spoofed
        ]

        imu_data = [
            {'acceleration': 0.3, 'heading': 90.0, 'velocity': 5.0},
            {'acceleration': 0.2, 'heading': 90.0, 'velocity': 5.3},
            {'acceleration': 0.1, 'heading': 90.0, 'velocity': 15.0},  # spoofed
            {'acceleration': 0.0, 'heading': 90.0, 'velocity': 15.1},  # spoofed
            {'acceleration': -0.1, 'heading': 270.0, 'velocity': 5.8},
            {'acceleration': 0.2, 'heading': 90.0, 'velocity': 20.0}   # spoofed
        ]

        velocity_detector = VelocityAnomalyDetector(threshold_velocity=30.0)
        fallback_manager = FallbackManager()

        spoof_flags, fallback_path = self._run_pipeline(gps_points, imu_data, velocity_detector, fallback_manager)

        # Check that spoofing is detected correctly
        assert len([f for f in spoof_flags if f]) >= 2, "Should detect multiple spoofing events"
        assert len(fallback_path) == len(gps_points)

    def test_empty_data_handling(self):
        """Test pipeline with empty or minimal data."""
        gps_points = []
        imu_data = []

        velocity_detector = VelocityAnomalyDetector(threshold_velocity=30.0)
        fallback_manager = FallbackManager()

        spoof_flags, fallback_path = self._run_pipeline(gps_points, imu_data, velocity_detector, fallback_manager)

        assert spoof_flags == []
        assert fallback_path == []

    def test_core_functionality_without_plotting(self):
        """Test core pipeline logic without matplotlib dependency."""
        # This test verifies the coordinate extraction works
        original, spoofed, corrected, attack_start, attack_end = create_demo_scenario()
        
        # Verify coordinate extraction and scenario creation works
        assert len(original) == len(spoofed) == len(corrected)
        assert attack_start < attack_end
        assert attack_start >= 0
        assert attack_end < len(original)

    def _run_pipeline(self, gps_points, imu_data, velocity_detector, fallback_manager):
        """Helper method to run the pipeline processing."""
        spoof_flags = []
        fallback_path = []

        for i in range(len(gps_points)):
            current = gps_points[i]
            spoofed = velocity_detector.detect(current)
            spoof_flags.append(spoofed)

            if spoofed and i > 0:
                dt = current['timestamp'] - gps_points[i-1]['timestamp']
                fallback_pos = fallback_manager.handle_fallback(gps_points[i-1], imu_data[i], dt)
                fallback_path.append(fallback_pos)
            else:
                fallback_path.append(None)

        return spoof_flags, fallback_path


def run_demo():
    """Interactive demo showcasing the complete pipeline visualization."""
    print("=== GPS Navigation Pipeline Demo ===\n")
    
    # Create realistic test scenario
    gps_points = [
        {'lat': 19.0760, 'lon': 72.8777, 'timestamp': 0},      # Start - Mumbai
        {'lat': 19.0762, 'lon': 72.8779, 'timestamp': 2},      # Normal movement
        {'lat': 19.0764, 'lon': 72.8781, 'timestamp': 4},      # Normal movement  
        {'lat': 19.0900, 'lon': 72.8850, 'timestamp': 6},      # Spoofed - sudden jump
        {'lat': 19.0902, 'lon': 72.8852, 'timestamp': 8},      # Spoofed - continued
        {'lat': 19.0904, 'lon': 72.8854, 'timestamp': 10},     # Spoofed - continued
        {'lat': 19.0768, 'lon': 72.8785, 'timestamp': 12},      # GPS restored
        {'lat': 19.0770, 'lon': 72.8787, 'timestamp': 14},      # Normal movement
        {'lat': 19.0772, 'lon': 72.8789, 'timestamp': 16}       # End point
    ]

    imu_data = [
        {'acceleration': 0.0, 'heading': 45.0, 'velocity': 0.0},
        {'acceleration': 0.2, 'heading': 45.0, 'velocity': 5.0},
        {'acceleration': 0.1, 'heading': 45.0, 'velocity': 5.5},
        {'acceleration': 0.0, 'heading': 45.0, 'velocity': 5.6},   # Spoofed - IMU shows consistent
        {'acceleration': 0.0, 'heading': 45.0, 'velocity': 5.7},   # Spoofed - IMU shows consistent
        {'acceleration': 0.0, 'heading': 45.0, 'velocity': 5.8},   # Spoofed - IMU shows consistent
        {'acceleration': -0.1, 'heading': 225.0, 'velocity': 5.5},  # GPS restored
        {'acceleration': 0.0, 'heading': 45.0, 'velocity': 5.6},
        {'acceleration': 0.0, 'heading': 45.0, 'velocity': 5.7}
    ]

    velocity_detector = VelocityAnomalyDetector(threshold_velocity=25.0)
    fallback_manager = FallbackManager()

    # Process pipeline
    spoof_flags = []
    fallback_path = []

    for i in range(len(gps_points)):
        current = gps_points[i]
        spoofed = velocity_detector.detect(current)
        spoof_flags.append(spoofed)

        if spoofed and i > 0:
            dt = current['timestamp'] - gps_points[i-1]['timestamp']
            fallback_pos = fallback_manager.handle_fallback(gps_points[i-1], imu_data[i], dt)
            fallback_path.append(fallback_pos)
            print(f"Point {i}: SPOOFED - Fallback activated")
        else:
            fallback_path.append(None)
            print(f"Point {i}: NORMAL - GPS signal trusted")

    # Generate basic report
    total_points = len(gps_points)
    spoofed_count = sum(spoof_flags)
    verified_count = total_points - spoofed_count
    integrity_ratio = (verified_count / total_points) * 100 if total_points > 0 else 0
    fallback_activations = len([f for f in fallback_path if f is not None])
    
    print(f"\n=== Navigation Report ===")
    print(f"Total Points: {total_points}")
    print(f"Verified GPS: {verified_count}")
    print(f"Spoofed Points: {spoofed_count}")
    print(f"Integrity Ratio: {integrity_ratio:.1f}%")
    print(f"Fallback Activations: {fallback_activations}")
    
    if spoofed_count > 0:
        print(f"Recommendations: GPS spoofing detected - IMU fallback system activated")

    # Visualize results using the available function
    print("\nGenerating visualization...")
    
    # Convert to format expected by plot_spoofing_scenario
    original_path = gps_points
    spoofed_path = []
    corrected_path = []
    
    for i, (gps_point, fallback) in enumerate(zip(gps_points, fallback_path)):
        spoofed_path.append(gps_point)  # Use actual GPS (including spoofed)
        if fallback is not None:
            corrected_path.append(fallback)
        else:
            corrected_path.append(gps_point)
    
    # Find attack indices
    attack_start = None
    attack_end = None
    for i, spoofed in enumerate(spoof_flags):
        if spoofed and attack_start is None:
            attack_start = i
        if spoofed:
            attack_end = i
    
    if attack_start is not None and attack_end is not None:
        plot_spoofing_scenario(original_path, spoofed_path, corrected_path, 
                             attack_start, attack_end,
                             title="GPS Spoofing Detection Demo - Mumbai Route")

    print("Demo completed successfully!")


if __name__ == "__main__":
    run_demo()
