"""GPS data generators for testing and demonstration purposes."""

import time
import random
from typing import Dict, Any, Iterator


class MockGpsGenerator:
    """
    Generates realistic mock GPS data for testing purposes.
    
    This generator creates a simulated GPS path with configurable spoofing
    patterns and realistic movement patterns.
    """
    
    def __init__(self, 
                 start_lat: float = 37.7749,
                 start_lon: float = -122.4194,
                 velocity_mps: float = 5.0,
                 spoof_rate: float = 0.1,
                 spoof_magnitude: float = 0.001):
        """
        Initialize the mock GPS generator.
        
        Args:
            start_lat: Starting latitude
            start_lon: Starting longitude
            velocity_mps: Base velocity in meters per second
            spoof_rate: Probability of generating spoofed points (0-1)
            spoof_magnitude: Magnitude of spoofing in degrees
        """
        self.current_lat = start_lat
        self.current_lon = start_lon
        self.velocity_mps = velocity_mps
        self.spoof_rate = spoof_rate
        self.spoof_magnitude = spoof_magnitude
        self.timestamp = time.time()
        self.point_count = 0
    
    def generate(self) -> Iterator[Dict[str, Any]]:
        """
        Generate continuous GPS data stream.
        
        Yields:
            Dict[str, Any]: GPS data point with:
                - 'latitude': Current latitude
                - 'longitude': Current longitude
                - 'timestamp': Unix timestamp
                - 'is_spoofed': Boolean indicating if point is spoofed
        """
        while True:
            self.point_count += 1
            
            # Generate next point
            next_point = self._generate_next_point()
            
            yield next_point
            
            # Simulate real-time delay
            time.sleep(0.1)
    
    def _generate_next_point(self) -> Dict[str, Any]:
        """Generate the next GPS point in sequence."""
        is_spoofed = random.random() < self.spoof_rate
        
        if not is_spoofed:
            # Normal movement
            bearing = random.uniform(0, 360)
            distance_m = self.velocity_mps * 1.0  # 1 second intervals
            
            # Calculate new position
            new_lat, new_lon = self._calculate_new_position(
                self.current_lat, self.current_lon, bearing, distance_m
            )
            
            self.current_lat = new_lat
            self.current_lon = new_lon
        else:
            # Spoofed point - add random offset
            spoof_lat = self.current_lat + random.uniform(
                -self.spoof_magnitude, self.spoof_magnitude
            )
            spoof_lon = self.current_lon + random.uniform(
                -self.spoof_magnitude, self.spoof_magnitude
            )
            
            self.current_lat = spoof_lat
            self.current_lon = spoof_lon
        
        self.timestamp = time.time()
        
        return {
            'latitude': self.current_lat,
            'longitude': self.current_lon,
            'timestamp': self.timestamp,
            'is_spoofed': is_spoofed
        }
    
    def _calculate_new_position(self, lat: float, lon: float, 
                               bearing_deg: float, distance_m: float) -> tuple[float, float]:
        """
        Calculate new position given bearing and distance.
        
        Args:
            lat: Starting latitude in degrees
            lon: Starting longitude in degrees
            bearing_deg: Bearing in degrees (0 = North)
            distance_m: Distance in meters
        
        Returns:
            tuple[float, float]: New (latitude, longitude) in degrees
        """
        # Convert to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing_deg)
        
        # Earth's radius in meters
        R = 6371000.0
        
        # Calculate new position
        angular_distance = distance_m / R
        
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(angular_distance) +
            math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
        )
        
        new_lon_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )
        
        # Convert back to degrees
        new_lat = math.degrees(new_lat_rad)
        new_lon = math.degrees(new_lon_rad)
        
        return new_lat, new_lon


def gps_data_src_mock() -> Iterator[Dict[str, Any]]:
    """
    Legacy compatibility function for mock GPS data.
    
    Returns:
        Iterator[Dict[str, Any]]: Mock GPS data stream
    """
    generator = MockGpsGenerator()
    return generator.generate()


# Import math for calculations
import math