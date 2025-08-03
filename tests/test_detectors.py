"""Tests for spoofing detection algorithms."""

import pytest
from gps_spoofing_detector.detectors import VelocityAnomalyDetector


class TestVelocityAnomalyDetector:
    """Test cases for VelocityAnomalyDetector."""
    
    def test_normal_velocity_not_detected(self):
        """Test that normal velocity changes are not detected as spoofing."""
        detector = VelocityAnomalyDetector(threshold_velocity=50.0)
        
        previous_point = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'timestamp': 1000.0
        }
        
        current_point = {
            'latitude': 37.7750,
            'longitude': -122.4195,
            'timestamp': 1001.0
        }
        
        detector.previous_point = previous_point
        result = detector.detect(current_point)
        assert result is False
    
    def test_extreme_velocity_detected(self):
        """Test that extreme velocity changes are detected as spoofing."""
        detector = VelocityAnomalyDetector(threshold_velocity=50.0)
        
        previous_point = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'timestamp': 1000.0
        }
        
        # Large jump in 1 second
        current_point = {
            'latitude': 37.7849,
            'longitude': -122.4094,
            'timestamp': 1001.0
        }
        
        detector.previous_point = previous_point
        result = detector.detect(current_point)
        assert result is True
    
    def test_first_point_not_detected(self):
        """Test that the first point (no previous) is not detected as spoofed."""
        detector = VelocityAnomalyDetector(threshold_velocity=50.0)
        
        current_point = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'timestamp': 1000.0
        }
        
        detector.reset()  # Ensure previous_point is None
        result = detector.detect(current_point)
        assert result is False
    
    def test_zero_time_interval(self):
        """Test handling of zero time interval."""
        detector = VelocityAnomalyDetector(threshold_velocity=50.0)
        
        previous_point = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'timestamp': 1000.0
        }
        
        current_point = {
            'latitude': 37.7849,
            'longitude': -122.4094,
            'timestamp': 1000.0  # Same timestamp
        }
        
        detector.previous_point = previous_point
        result = detector.detect(current_point)
        assert result is False