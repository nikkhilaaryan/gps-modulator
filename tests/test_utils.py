"""Tests for utility functions."""

import pytest
import math
from gps_spoofing_detector.utils import (
    haversine_distance, 
    compute_velocity, 
    validate_coordinates,
    bearing
)


class TestHaversineDistance:
    """Test cases for haversine distance calculation."""
    
    def test_same_point_distance(self):
        """Test distance between identical points is zero."""
        distance = haversine_distance(37.7749, -122.4194, 37.7749, -122.4194)
        assert abs(distance) < 1.0  # Should be very close to zero
    
    def test_known_distance(self):
        """Test distance calculation against known values."""
        # Distance between San Francisco and Los Angeles
        distance = haversine_distance(37.7749, -122.4194, 34.0522, -118.2437)
        expected_distance = 559000  # ~559 km
        assert abs(distance - expected_distance) < 10000  # Within 10km tolerance


class TestComputeVelocity:
    """Test cases for velocity computation."""
    
    def test_normal_velocity_calculation(self):
        """Test velocity calculation with valid data."""
        previous = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'timestamp': 0.0
        }
        current = {
            'latitude': 37.7750,
            'longitude': -122.4195,
            'timestamp': 1.0
        }
        
        velocity = compute_velocity(previous, current)
        assert velocity > 0  # Should be positive
        assert velocity < 100  # Should be reasonable
    
    def test_zero_time_interval(self):
        """Test velocity with zero time interval."""
        previous = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'timestamp': 1000.0
        }
        current = {
            'latitude': 37.7750,
            'longitude': -122.4195,
            'timestamp': 1000.0
        }
        
        velocity = compute_velocity(previous, current)
        assert velocity == 0.0
    
    def test_none_previous_point(self):
        """Test velocity with no previous point."""
        current = {
            'latitude': 37.7749,
            'longitude': -122.4194,
            'timestamp': 1000.0
        }
        
        velocity = compute_velocity(None, current)
        assert velocity == 0.0


class TestValidateCoordinates:
    """Test cases for coordinate validation."""
    
    def test_valid_coordinates(self):
        """Test valid coordinate ranges."""
        assert validate_coordinates(37.7749, -122.4194) is True
        assert validate_coordinates(0, 0) is True
        assert validate_coordinates(-33.8688, 151.2093) is True  # Sydney
    
    def test_invalid_latitude(self):
        """Test invalid latitude values."""
        assert validate_coordinates(91, 0) is False  # Too high
        assert validate_coordinates(-91, 0) is False  # Too low
    
    def test_invalid_longitude(self):
        """Test invalid longitude values."""
        assert validate_coordinates(0, 181) is False  # Too high
        assert validate_coordinates(0, -181) is False  # Too low


class TestBearing:
    """Test cases for bearing calculation."""
    
    def test_north_bearing(self):
        """Test bearing calculation for north direction."""
        bearing_deg = bearing(37.7749, -122.4194, 37.7849, -122.4194)
        assert abs(bearing_deg - 0) < 5  # Should be close to 0 degrees
    
    def test_east_bearing(self):
        """Test bearing calculation for east direction."""
        bearing_deg = bearing(37.7749, -122.4194, 37.7749, -122.4094)
        assert abs(bearing_deg - 90) < 5  # Should be close to 90 degrees