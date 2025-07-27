from typing import Dict
from gps_modulator.fallback.dead_reckoner import DeadReckoner

class FallbackManager:
    def __init__(self):
        self.fallback_active = False
        self.last_position = None
        self.reckoner = None
    
    def handle_fallback(self, present_position: Dict[str, float], imu_data: Dict[str, float], delta_time: float) -> Dict[str, float]:
        if not self.fallback_active:
            self.fallback_active = True
            self.last_position = present_position
            
            initial_velocity = imu_data.get('velocity', 0.0)
            self.reckoner = DeadReckoner(initial_position=present_position, initial_velocity=initial_velocity)

            estimated_position = self.reckoner.update(imu_data, delta_time)
            return estimated_position

    def handle_gps_restored(self, next_gps_position: Dict[str, float]):
        if self.fallback_active:
            self.fallback_active = False
            self.last_position = next_gps_position
            self.reckoner = None

    def is_fallback_active(self) -> bool:
        return self.fallback_active

 
            
            
