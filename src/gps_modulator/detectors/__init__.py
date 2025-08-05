"""GPS Spoofing Detection Algorithms.

This module contains various algorithms for detecting GPS spoofing attacks.
"""

from .velocity_anomaly_detector import VelocityAnomalyDetector

__all__ = ["VelocityAnomalyDetector"]