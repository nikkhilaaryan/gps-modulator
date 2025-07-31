import math
from typing import Dict

class DeadReckoner:
    def __init__(self,initial_position: Dict[str, float], initial_velocity: float):
        self.position = initial_position
        self.velocity = initial_velocity

    def update(self, imu_data: Dict[str,float], delta_time: float) -> Dict[str, float]:
        # Use provided velocity or calculate from acceleration if available
        if 'acceleration' in imu_data:
            acceleration = imu_data['acceleration']
            self.velocity += acceleration * delta_time
        else:
            # If no acceleration, use provided velocity directly
            self.velocity = imu_data.get('velocity', self.velocity)
        
        heading = imu_data['heading']
        distance = self.velocity * delta_time

        next_position = self.compute_next_position(self.position,heading,distance)
        self.position = next_position

        return next_position

    def compute_next_position(self, present_position: Dict[str, float], heading: float, distance: float) -> Dict[str, float]:
        R = 6371000 #Earth's Radius 

        # Handle both 'lat/lon' and 'latitude/longitude' key formats
        lat = present_position.get('lat', present_position.get('latitude', 0.0))
        lon = present_position.get('lon', present_position.get('longitude', 0.0))

        delta_lat = (distance * math.cos(math.radians(heading)) / R)
        delta_lon = (distance * math.sin(math.radians(heading))) /(R * math.cos(math.radians(lat)))
        
        next_lat = lat + math.degrees(delta_lat)
        next_lon = lon + math.degrees(delta_lon)

        return {'latitude': next_lat, 'longitude': next_lon}








