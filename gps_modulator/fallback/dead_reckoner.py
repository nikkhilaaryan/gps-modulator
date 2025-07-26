import math
from typing import Dict

class DeadReckoner:
    def __init__(self,initial_position: Dict[str, float], initial_velocity: float):
        self.position = initial_position
        self.velocity = initial_velocity

    def update(self, imu_data: Dict[str,float], delta_time: float) -> Dict[str, float]:
        acceleration = imu_data['acceleration']
        heading = imu_data['heading']

        self.velocity += acceleration * delta_time
        distance = self.velocity * delta_time

        next_position = self.compute_next_position(self.position,heading,distance)
        self.position = next_position

        return next_position

    def compute_next_position(self, present_position: Dict[str, float], heading: float, distance: float) -> Dict[str, float]:
        R = 6371000 #Earth's Radius 

        delta_lat = (distance * math.cos(math.radians(heading)) / R)
        delta_lon = (distance * math.sin(math.radians(heading))) /(R * math.cos(math.radians(present_position['lat'])))
        
        next_lat = present_position['lat'] + math.degrees(delta_lat)
        next_lon = present_position['lon'] + math.degrees(delta_lon)

        return {'lat': next_lat, 'lon': next_lon}








