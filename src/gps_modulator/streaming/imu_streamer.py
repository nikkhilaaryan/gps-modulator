"""IMU data streaming and generation for GPS spoofing detection integration."""

import time
import random
import math
from typing import Dict, Any, Iterator, Optional
from ..correction.imu_handler import MockIMUGenerator, EnhancedIMUHandler


class IMUStreamer:
    """Real-time IMU data streaming for GPS integration."""
    
    def __init__(self, update_rate: float = 10.0) -> None:
        """
        Initialize IMU streamer.
        
        Args:
            update_rate: Updates per second (Hz)
        """
        self.update_rate = update_rate
        self.update_interval = 1.0 / update_rate
        self.mock_generator = MockIMUGenerator()
        self.last_heading = 0.0
        self.last_timestamp = 0.0
    
    def stream_imu_data(self) -> Iterator[Dict[str, float]]:
        """
        Stream real-time IMU data.
        
        Yields:
            Dict[str, float]: IMU data with timestamp
        """
        while True:
            timestamp = time.time()
            
            # Simulate gradual heading changes
            heading_change = random.uniform(-5.0, 5.0)  # degrees per second
            
            imu_data = self.mock_generator.generate_data(timestamp, heading_change)
            
            yield imu_data
            
            # Sleep to maintain update rate
            time.sleep(self.update_interval)
    
    def get_imu_data(self) -> Dict[str, float]:
        """
        Get single IMU data point.
        
        Returns:
            Dict[str, float]: Current IMU readings
        """
        timestamp = time.time()
        heading_change = random.uniform(-2.0, 2.0)
        return self.mock_generator.generate_data(timestamp, heading_change)


class EnhancedGpsReader:
    """Enhanced GPS reader that integrates GPS and IMU data."""
    
    def __init__(self, use_imu: bool = True, imu_rate: float = 10.0) -> None:
        """
        Initialize enhanced GPS reader.
        
        Args:
            use_imu: Whether to include IMU data
            imu_rate: IMU update rate in Hz
        """
        self.use_imu = use_imu
        self.imu_streamer = IMUStreamer(imu_rate) if use_imu else None
        self.imu_handler = EnhancedIMUHandler() if use_imu else None
    
    def read_enhanced_data(self, gps_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read GPS data enhanced with IMU information.
        
        Args:
            gps_data: Basic GPS data dictionary
        
        Returns:
            Dict[str, Any]: Enhanced data with IMU integration
        """
        enhanced_data = gps_data.copy()
        
        if self.use_imu and self.imu_streamer:
            # Get current IMU data
            imu_data = self.imu_streamer.get_imu_data()
            
            # Process IMU data if handler is available
            if self.imu_handler:
                processed_imu = self.imu_handler.process_imu_data(imu_data)
                enhanced_data['imu'] = {
                    'raw': imu_data,
                    'processed': {
                        'heading': processed_imu.heading,
                        'pitch': processed_imu.pitch,
                        'roll': processed_imu.roll,
                        'acceleration': math.sqrt(
                            processed_imu.acceleration_x**2 + 
                            processed_imu.acceleration_y**2
                        )
                    }
                }
            else:
                enhanced_data['imu'] = imu_data
        
        return enhanced_data


class MockIMUDataGenerator:
    """Advanced mock IMU data generator for testing scenarios."""
    
    def __init__(self) -> None:
        """Initialize mock generator with realistic parameters."""
        self.current_time = 0.0
        self.position = {'lat': 40.7128, 'lon': -74.0060}  # NYC coordinates
        self.velocity = 10.0  # m/s
        self.heading = 45.0  # degrees
        self.pitch = 0.0
        self.roll = 0.0
        
        # Noise parameters
        self.accel_noise = 0.1
        self.gyro_noise = 0.05
        self.mag_noise = 0.02
    
    def generate_vehicle_motion(self, 
                               duration: float, 
                               speed_profile: Optional[list] = None,
                               heading_changes: Optional[list] = None) -> Iterator[Dict[str, float]]:
        """
        Generate realistic vehicle motion IMU data.
        
        Args:
            duration: Duration in seconds
            speed_profile: List of (time, speed) tuples
            heading_changes: List of (time, heading_change) tuples
        
        Yields:
            Dict[str, float]: Realistic IMU data
        """
        dt = 0.1  # 10Hz update rate
        steps = int(duration / dt)
        
        for step in range(steps):
            current_time = step * dt
            
            # Update speed based on profile
            if speed_profile:
                speed = np.interp(current_time, [p[0] for p in speed_profile], [p[1] for p in speed_profile])
            else:
                speed = self.velocity + random.uniform(-1.0, 1.0)
            
            # Update heading based on changes
            if heading_changes:
                heading_change = np.interp(current_time, [h[0] for h in heading_changes], [h[1] for h in heading_changes])
            else:
                heading_change = random.uniform(-2.0, 2.0)
            
            self.heading = (self.heading + heading_change * dt) % 360
            
            # Generate realistic IMU readings
            accel_x = random.normalvariate(0, self.accel_noise)
            accel_y = random.normalvariate(0, self.accel_noise)
            accel_z = 9.81 + random.normalvariate(0, self.accel_noise)
            
            gyro_x = random.normalvariate(0, self.gyro_noise)
            gyro_y = random.normalvariate(0, self.gyro_noise)
            gyro_z = heading_change + random.normalvariate(0, self.gyro_noise)
            
            # Calculate magnetic field
            heading_rad = math.radians(self.heading)
            mag_x = math.cos(heading_rad) + random.normalvariate(0, self.mag_noise)
            mag_y = math.sin(heading_rad) + random.normalvariate(0, self.mag_noise)
            mag_z = 0.5 + random.normalvariate(0, self.mag_noise)
            
            yield {
                'accel_x': accel_x,
                'accel_y': accel_y,
                'accel_z': accel_z,
                'gyro_x': gyro_x,
                'gyro_y': gyro_y,
                'gyro_z': gyro_z,
                'mag_x': mag_x,
                'mag_y': mag_y,
                'mag_z': mag_z,
                'timestamp': current_time
            }


# Convenience function for integration
def create_imu_enhanced_system(use_imu: bool = True) -> tuple:
    """
    Create enhanced GPS system with IMU integration.
    
    Args:
        use_imu: Whether to enable IMU integration
    
    Returns:
        tuple: (EnhancedGpsReader, EnhancedIMUHandler)
    """
    from ..correction.path_corrector import PathCorrector
    
    gps_reader = EnhancedGpsReader(use_imu=use_imu)
    path_corrector = PathCorrector()
    
    if use_imu:
        path_corrector.enable_imu_correction()
    
    return gps_reader, path_corrector