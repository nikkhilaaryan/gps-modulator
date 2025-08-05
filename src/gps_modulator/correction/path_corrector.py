"""GPS path correction using dead reckoning and fallback strategies."""

from typing import Dict, Any, Optional
from .dead_reckoner import DeadReckoner
from .imu_handler import EnhancedIMUHandler, IMUData


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
        self.imu_handler: Optional[EnhancedIMUHandler] = None
        self.use_imu_correction: bool = False  # Default to False
        self.imu_calibration_data: Optional[Dict[str, Any]] = None
    
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
        if self.use_imu_correction and imu_data:
            return self._apply_imu_correction(current_point, imu_data)
        else:
            return self._apply_basic_correction(current_point, imu_data)
    
    def enable_imu_correction(self, calibration_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Enable IMU-based correction with optional calibration.
        
        Args:
            calibration_data: Optional IMU calibration data
        """
        self.imu_handler = EnhancedIMUHandler()
        self.use_imu_correction = True
        
        if calibration_data:
            self.imu_handler.calibrate(calibration_data)
            self.imu_calibration_data = calibration_data
    
    def disable_imu_correction(self) -> None:
        """Disable IMU-based correction."""
        self.use_imu_correction = False
        self.imu_handler = None
    
    def set_magnetic_declination(self, declination: float) -> None:
        """Set local magnetic declination for compass correction."""
        if self.imu_handler:
            self.imu_handler.set_magnetic_declination(declination)
    
    def _apply_imu_correction(self, 
                            current_point: Dict[str, Any],
                            imu_data: Dict[str, float]) -> Dict[str, float]:
        """Apply advanced IMU-based correction."""
        if not self.imu_handler or not self.use_imu_correction:
            return self._apply_basic_correction(current_point, imu_data)
        
        try:
            # Process IMU data
            processed_imu = self.imu_handler.process_imu_data(imu_data)
            
            # Calculate time delta
            time_delta = current_point['timestamp'] - self.last_valid_position['timestamp']
            
            if time_delta <= 0:
                return self.last_valid_position.copy()
            
            # Get motion vector from enhanced IMU processing
            motion_vector = self.imu_handler.get_motion_vector(processed_imu, time_delta)
            
            # Use dead reckoner with enhanced data
            if self.dead_reckoner is None:
                self.dead_reckoner = DeadReckoner(
                    initial_position=self.last_valid_position,
                    initial_velocity=motion_vector.get('speed', 0.0)
                )
            
            # Update dead reckoner with IMU data
            corrected = self.dead_reckoner.update(processed_imu.__dict__, time_delta)
            
            return {
                'latitude': corrected['latitude'],
                'longitude': corrected['longitude'],
                'timestamp': current_point['timestamp'],
                'confidence': 0.9,  # High confidence with IMU data
                'correction_method': 'imu_enhanced'
            }
            
        except Exception as e:
            # Fallback to basic correction on IMU processing errors
            return self._apply_basic_correction(current_point, imu_data)
    
    def _apply_basic_correction(self, 
                              current_point: Dict[str, Any],
                              imu_data: Optional[Dict[str, float]]) -> Dict[str, float]:
        """Apply basic dead reckoning correction (existing logic)."""
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
                'timestamp': current_point['timestamp'],
                'confidence': 0.7,  # Medium confidence with basic IMU
                'correction_method': 'basic_dead_reckoning'
            }
        else:
            # Fallback: return last known good position
            return {
                'latitude': self.last_valid_position['latitude'],
                'longitude': self.last_valid_position['longitude'],
                'timestamp': current_point['timestamp'],
                'confidence': 0.3,  # Low confidence with fallback
                'correction_method': 'position_hold'
            }
    
    def reset(self) -> None:
        """Reset the corrector's state."""
        self.last_valid_position = None
        self.dead_reckoner = None
        if self.imu_handler:
            self.imu_handler = EnhancedIMUHandler()
            if self.imu_calibration_data:
                self.imu_handler.calibrate(self.imu_calibration_data)