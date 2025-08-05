"""Enhanced IMU data handling and integration for GPS path correction."""

import math
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class IMUData:
    """Structured IMU data container."""
    
    # Accelerometer data (m/s²)
    acceleration_x: float = 0.0
    acceleration_y: float = 0.0
    acceleration_z: float = 0.0
    
    # Gyroscope data (degrees/second)
    gyro_x: float = 0.0
    gyro_y: float = 0.0
    gyro_z: float = 0.0
    
    # Magnetometer/compass data (microtesla)
    mag_x: float = 0.0
    mag_y: float = 0.0
    mag_z: float = 0.0
    
    # Computed values
    heading: float = 0.0  # degrees from magnetic north
    pitch: float = 0.0   # degrees
    roll: float = 0.0    # degrees
    
    # Timestamp
    timestamp: float = 0.0


class EnhancedIMUHandler:
    """Advanced IMU data processing for improved GPS path correction."""
    
    def __init__(self) -> None:
        """Initialize the IMU handler."""
        self.previous_imu_data: Optional[IMUData] = None
        self.magnetic_declination: float = 0.0  # Local magnetic declination
        
        # Calibration data
        self.accel_bias = np.array([0.0, 0.0, 0.0])
        self.gyro_bias = np.array([0.0, 0.0, 0.0])
        self.mag_bias = np.array([0.0, 0.0, 0.0])
        
        # Filtering
        self.alpha = 0.8  # Complementary filter coefficient
        self.heading_history = []
        self.max_history = 10
    
    def calibrate(self, calibration_data: Dict[str, np.ndarray]) -> None:
        """
        Calibrate IMU sensors using provided calibration data.
        
        Args:
            calibration_data: Dictionary with 'accel', 'gyro', 'mag' arrays
        """
        if 'accel' in calibration_data:
            self.accel_bias = np.mean(calibration_data['accel'], axis=0)
        if 'gyro' in calibration_data:
            self.gyro_bias = np.mean(calibration_data['gyro'], axis=0)
        if 'mag' in calibration_data:
            self.mag_bias = np.mean(calibration_data['mag'], axis=0)
    
    def process_imu_data(self, raw_data: Dict[str, float]) -> IMUData:
        """
        Process raw IMU data into structured format.
        
        Args:
            raw_data: Dictionary with raw sensor readings
        
        Returns:
            IMUData: Processed and calibrated IMU data
        """
        # Apply calibration
        accel = np.array([
            raw_data.get('accel_x', 0.0) - self.accel_bias[0],
            raw_data.get('accel_y', 0.0) - self.accel_bias[1],
            raw_data.get('accel_z', 0.0) - self.accel_bias[2]
        ])
        
        gyro = np.array([
            raw_data.get('gyro_x', 0.0) - self.gyro_bias[0],
            raw_data.get('gyro_y', 0.0) - self.gyro_bias[1],
            raw_data.get('gyro_z', 0.0) - self.gyro_bias[2]
        ])
        
        mag = np.array([
            raw_data.get('mag_x', 0.0) - self.mag_bias[0],
            raw_data.get('mag_y', 0.0) - self.mag_bias[1],
            raw_data.get('mag_z', 0.0) - self.mag_bias[2]
        ])
        
        # Calculate attitude angles
        pitch, roll = self._calculate_attitude(accel)
        heading = self._calculate_heading(mag, pitch, roll)
        
        # Apply complementary filtering for smooth heading
        if self.previous_imu_data:
            dt = raw_data.get('timestamp', 0.0) - self.previous_imu_data.timestamp
            if dt > 0:
                # Gyro integration for short-term stability
                gyro_heading = self.previous_imu_data.heading + gyro[2] * dt
                # Magnetometer for long-term stability
                heading = self.alpha * gyro_heading + (1 - self.alpha) * heading
        
        # Smooth heading using moving average
        self.heading_history.append(heading)
        if len(self.heading_history) > self.max_history:
            self.heading_history.pop(0)
        
        if self.heading_history:
            heading = np.mean(self.heading_history)
        
        imu_data = IMUData(
            acceleration_x=accel[0],
            acceleration_y=accel[1],
            acceleration_z=accel[2],
            gyro_x=gyro[0],
            gyro_y=gyro[1],
            gyro_z=gyro[2],
            mag_x=mag[0],
            mag_y=mag[1],
            mag_z=mag[2],
            heading=heading,
            pitch=pitch,
            roll=roll,
            timestamp=raw_data.get('timestamp', 0.0)
        )
        
        self.previous_imu_data = imu_data
        return imu_data
    
    def _calculate_attitude(self, accel: np.ndarray) -> Tuple[float, float]:
        """Calculate pitch and roll from accelerometer data."""
        # Normalize accelerometer data
        accel_norm = accel / np.linalg.norm(accel)
        
        # Calculate pitch and roll
        pitch = math.degrees(math.atan2(accel_norm[0], math.sqrt(accel_norm[1]**2 + accel_norm[2]**2)))
        roll = math.degrees(math.atan2(accel_norm[1], math.sqrt(accel_norm[0]**2 + accel_norm[2]**2)))
        
        return pitch, roll
    
    def _calculate_heading(self, mag: np.ndarray, pitch: float, roll: float) -> float:
        """Calculate heading from magnetometer data with tilt compensation."""
        # Tilt compensation
        pitch_rad = math.radians(pitch)
        roll_rad = math.radians(roll)
        
        # Apply tilt compensation
        mag_x = mag[0] * math.cos(pitch_rad) + mag[2] * math.sin(pitch_rad)
        mag_y = mag[0] * math.sin(roll_rad) * math.sin(pitch_rad) + \
                mag[1] * math.cos(roll_rad) - mag[2] * math.sin(roll_rad) * math.cos(pitch_rad)
        
        # Calculate heading
        heading = math.degrees(math.atan2(mag_y, mag_x))
        
        # Convert to 0-360 range
        if heading < 0:
            heading += 360
        
        # Apply magnetic declination correction
        heading = (heading + self.magnetic_declination) % 360
        
        return heading
    
    def get_motion_vector(self, imu_data: IMUData, delta_time: float) -> Dict[str, float]:
        """
        Calculate motion vector from IMU data.
        
        Args:
            imu_data: Processed IMU data
            delta_time: Time since last update in seconds
        
        Returns:
            Dict with 'heading', 'speed', 'acceleration'
        """
        # Calculate speed from acceleration integration
        if self.previous_imu_data:
            # Use horizontal acceleration for speed calculation
            accel_horizontal = math.sqrt(imu_data.acceleration_x**2 + imu_data.acceleration_y**2)
            speed = accel_horizontal * delta_time
        else:
            speed = 0.0
        
        return {
            'heading': imu_data.heading,
            'speed': speed,
            'acceleration': math.sqrt(imu_data.acceleration_x**2 + imu_data.acceleration_y**2)
        }
    
    def set_magnetic_declination(self, declination: float) -> None:
        """Set local magnetic declination in degrees."""
        self.magnetic_declination = declination


class MockIMUGenerator:
    """Generate simulated IMU data for testing."""
    
    def __init__(self, initial_heading: float = 0.0, noise_level: float = 0.1):
        """Initialize mock IMU generator."""
        self.current_heading = initial_heading
        self.noise_level = noise_level
        self.last_timestamp = 0.0
        
    def generate_data(self, timestamp: float, heading_change: float = 0.0) -> Dict[str, float]:
        """
        Generate mock IMU data.
        
        Args:
            timestamp: Current timestamp
            heading_change: Change in heading (degrees/second)
        
        Returns:
            Dict[str, float]: Simulated IMU data
        """
        delta_time = timestamp - self.last_timestamp if self.last_timestamp > 0 else 0.1
        
        # Update heading
        self.current_heading = (self.current_heading + heading_change * delta_time) % 360
        
        # Add noise
        noise = lambda: np.random.normal(0, self.noise_level)
        
        data = {
            'accel_x': noise(),
            'accel_y': noise(),
            'accel_z': 9.81 + noise(),  # Gravity
            'gyro_x': noise(),
            'gyro_y': noise(),
            'gyro_z': heading_change + noise(),
            'mag_x': math.cos(math.radians(self.current_heading)) + noise(),
            'mag_y': math.sin(math.radians(self.current_heading)) + noise(),
            'mag_z': 0.5 + noise(),
            'timestamp': timestamp
        }
        
        self.last_timestamp = timestamp
        return data