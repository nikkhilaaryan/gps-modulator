"""
GPS Spoofing Detection and Correction System

A comprehensive Python package for real-time GPS spoofing detection and path correction.

This package provides:
- Real-time GPS spoofing detection using velocity anomaly detection
- Path correction using dead reckoning and fallback strategies
- Live visualization of GPS tracks
- Streaming GPS data processing
- Modular architecture for easy integration

Modules:
    core: Core detection and correction pipeline
    detectors: GPS spoofing detection algorithms
    correction: Path correction strategies
    streaming: GPS data streaming and reading
    visualization: Real-time plotting and visualization
    utils: Utility functions and helpers
"""

__version__ = "1.0.0"
__author__ = "GPS Spoofing Detection Team"
__email__ = "contact@example.com"

from .detectors.velocity_anomaly_detector import VelocityAnomalyDetector
from .correction.path_corrector import PathCorrector
from .streaming.gps_reader import GpsReader
from .visualization.live_plotter import LivePathPlotter

__all__ = [
    "VelocityAnomalyDetector",
    "PathCorrector", 
    "GpsReader",
    "LivePathPlotter"
]