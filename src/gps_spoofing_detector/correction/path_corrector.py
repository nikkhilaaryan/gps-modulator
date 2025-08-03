"""GPS path correction using dead reckoning and fallback strategies."""

from typing import Dict, Any, Optional
from .dead_reckoner import DeadReckoner


class PathCorrector:
    """
    Corrects GPS paths when spoofing is detected.
    
    This class provides strategies for correcting GPS coordinates when
    spoofing is detected, using dead reckoning based on IMU data or
    fallback to the last known good position.
    
    Attributes:
        last_valid_position (Optional[Dict[str, float]]): Last known good GPS position
        dead_reckoner (Optional[DeadReckoner]): Dead reckoning calculator
    """
    
    def __init__(self) -> None:
        """Initialize the path corrector."""
        self.last_valid_position: Optional[Dict[str, float]] = None
        self.dead_reckoner: Optional[DeadReckoner] = None
    
    def correct(self, 
                current_point: Dict[str, Any], 
                is_spoofed: bool = False,
                imu_data: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Correct a GPS point if it's detected as spoofed.
        
        Args:
            current_point: Dictionary with GPS data containing:
                - 'latitude' (float): Latitude in decimal degrees
                - 'longitude' (float): Longitude in decimal degrees  
                - 'timestamp' (float): Unix timestamp
            is_spoofed: Whether this point is detected as spoofed
            imu_data: Optional IMU data dictionary with:
                - 'heading' (float): Heading in degrees (0-360)
                - 'speed' (float): Speed in m/s
                - 'acceleration' (float): Optional acceleration in m/s²
        
        Returns:
            Dict[str, float]: Corrected GPS coordinates with keys:
                'latitude', 'longitude', 'timestamp'
        """
        if self.last_valid_position is None:
            self.last_valid_position = {
                'latitude': current_point['latitude'],
                'longitude': current_point['longitude'],
                'timestamp': current_point['timestamp']
            }
            return self.last_valid_position.copy()
        
        if not is_spoofed:
            # Point is valid, update last known position
            self.last_valid_position = {
                'latitude': current_point['latitude'],
                'longitude': current_point['longitude'],
                'timestamp': current_point['timestamp']
            }
            return self.last_valid_position.copy()
        
        # Point is spoofed, apply correction
        return self._apply_correction(current_point, imu_data)
    
    def _apply_correction(self, 
                         current_point: Dict[str, Any],
                         imu_data: Optional[Dict[str, float]]) -> Dict[str, float]:
        """Apply correction strategy for spoofed points."""
        # Initialize dead reckoner if needed
        if self.dead_reckoner is None:
            self.dead_reckoner = DeadReckoner(
                initial_position=self.last_valid_position,
                initial_velocity=0.0
            )
        
        # Use dead reckoning if IMU data is available
        if imu_data and 'heading' in imu_data and 'speed' in imu_data:
            heading = imu_data['heading']
            speed = imu_data['speed']
            
            time_delta = current_point['timestamp'] - self.last_valid_position['timestamp']
            distance = speed * time_delta
            
            corrected = self.dead_reckoner.compute_next_position(
                self.last_valid_position, heading, distance
            )
            
            return {
                'latitude': corrected['latitude'],
                'longitude': corrected['longitude'],
                'timestamp': current_point['timestamp']
            }
        else:
            # Fallback: return last known good position
            return {
                'latitude': self.last_valid_position['latitude'],
                'longitude': self.last_valid_position['longitude'],
                'timestamp': current_point['timestamp']
            }
    
    def reset(self) -> None:
        """Reset the corrector's state."""
        self.last_valid_position = None
        self.dead_reckoner = None