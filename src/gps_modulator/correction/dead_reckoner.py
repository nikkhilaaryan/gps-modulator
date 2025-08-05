"""Dead reckoning navigation for GPS path correction."""

import math
from typing import Dict, Any, Optional


class DeadReckoner:
    """
    Dead reckoning navigation system for estimating position without GPS.
    
    Uses heading and distance measurements to estimate the next position
    based on the last known position.
    
    Attributes:
        current_position (Dict[str, float]): Current estimated position
        current_velocity (float): Current velocity in m/s
        earth_radius (float): Earth's radius in meters
    """
    
    EARTH_RADIUS = 6371000.0  # Earth's radius in meters
    
    def __init__(self, initial_position: Dict[str, float], initial_velocity: float = 0.0) -> None:
        """
        Initialize the dead reckoner.
        
        Args:
            initial_position: Dictionary with initial position:
                - 'latitude' (float): Initial latitude in decimal degrees
                - 'longitude' (float): Initial longitude in decimal degrees
            initial_velocity: Initial velocity in m/s (default: 0.0)
        """
        self.current_position = {
            'latitude': float(initial_position.get('latitude', initial_position.get('lat', 0.0))),
            'longitude': float(initial_position.get('longitude', initial_position.get('lon', 0.0)))
        }
        self.current_velocity = float(initial_velocity)
    
    def update(self, imu_data: Dict[str, float], delta_time: float) -> Dict[str, float]:
        """
        Update position based on IMU data.
        
        Args:
            imu_data: Dictionary with IMU measurements:
                - 'heading' (float): Heading in degrees (0-360)
                - 'speed' (float): Speed in m/s
                - 'acceleration' (float): Optional acceleration in m/s²
            delta_time: Time elapsed since last update in seconds
        
        Returns:
            Dict[str, float]: Updated position with 'latitude' and 'longitude'
        """
        # Update velocity based on acceleration if available
        if 'acceleration' in imu_data:
            acceleration = float(imu_data['acceleration'])
            self.current_velocity += acceleration * delta_time
        else:
            # Use provided speed directly
            self.current_velocity = float(imu_data.get('speed', self.current_velocity))
        
        heading = float(imu_data['heading'])
        distance = self.current_velocity * delta_time
        
        next_position = self.compute_next_position(
            self.current_position, heading, distance
        )
        
        self.current_position = next_position
        return next_position.copy()
    
    def compute_next_position(self, 
                             present_position: Dict[str, float],
                             heading: float,
                             distance: float) -> Dict[str, float]:
        """
        Compute the next position given heading and distance.
        
        Args:
            present_position: Current position dictionary with 'latitude' and 'longitude'
            heading: Heading in degrees (0-360, where 0 is North)
            distance: Distance to travel in meters
        
        Returns:
            Dict[str, float]: Next position with 'latitude' and 'longitude'
        """
        # Extract coordinates with fallback for different key names
        lat = float(present_position.get('latitude', present_position.get('lat', 0.0)))
        lon = float(present_position.get('longitude', present_position.get('lon', 0.0)))
        
        # Convert to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        heading_rad = math.radians(heading)
        
        # Calculate angular distance
        angular_distance = distance / self.EARTH_RADIUS
        
        # Calculate new latitude
        new_lat_rad = math.asin(
            math.sin(lat_rad) * math.cos(angular_distance) +
            math.cos(lat_rad) * math.sin(angular_distance) * math.cos(heading_rad)
        )
        
        # Calculate new longitude
        new_lon_rad = lon_rad + math.atan2(
            math.sin(heading_rad) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat_rad)
        )
        
        # Convert back to degrees
        new_lat = math.degrees(new_lat_rad)
        new_lon = math.degrees(new_lon_rad)
        
        # Normalize longitude to -180 to 180 range
        new_lon = ((new_lon + 180) % 360) - 180
        
        return {'latitude': new_lat, 'longitude': new_lon}
    
    def get_current_position(self) -> Dict[str, float]:
        """Get the current estimated position."""
        return self.current_position.copy()
    
    def get_current_velocity(self) -> float:
        """Get the current velocity."""
        return self.current_velocity
    
    def reset(self, new_position: Optional[Dict[str, float]] = None) -> None:
        """
        Reset the dead reckoner with a new position.
        
        Args:
            new_position: New position to reset to (optional)
        """
        if new_position is not None:
            self.current_position = {
                'latitude': float(new_position.get('latitude', new_position.get('lat', 0.0))),
                'longitude': float(new_position.get('longitude', new_position.get('lon', 0.0)))
            }
        self.current_velocity = 0.0