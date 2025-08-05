"""Velocity-based GPS spoofing detection."""

from typing import Dict, Any, Optional
from ..utils.gps_math import compute_velocity


class VelocityAnomalyDetector:
    """
    Detects GPS spoofing attacks based on unrealistic velocity changes.
    
    This detector analyzes the velocity between consecutive GPS points and
    flags points as potentially spoofed if the calculated velocity exceeds
    a reasonable threshold.
    
    Attributes:
        threshold_velocity (float): Maximum realistic velocity in m/s
        previous_point (Optional[Dict[str, Any]]): Last valid GPS point
    """
    
    def __init__(self, threshold_velocity: float = 30.0) -> None:
        """
        Initialize the velocity anomaly detector.
        
        Args:
            threshold_velocity: Maximum realistic velocity in m/s (default: 30.0)
        """
        self.threshold_velocity: float = threshold_velocity
        self.previous_point: Optional[Dict[str, Any]] = None
    
    def detect(self, current_point: Dict[str, Any]) -> bool:
        """
        Detect if the current GPS point indicates spoofing.
        
        Args:
            current_point: Dictionary containing GPS data with keys:
                - 'latitude' (float): Latitude in decimal degrees
                - 'longitude' (float): Longitude in decimal degrees
                - 'timestamp' (float): Unix timestamp
        
        Returns:
            bool: True if spoofing is detected, False otherwise
        """
        if self.previous_point is None:
            self.previous_point = current_point
            return False
        
        velocity = compute_velocity(self.previous_point, current_point)
        self.previous_point = current_point
        
        return velocity > self.threshold_velocity
    
    def reset(self) -> None:
        """Reset the detector's state."""
        self.previous_point = None