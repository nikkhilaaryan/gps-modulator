from typing import Dict, Any
from gps_modulator.core.detection_pipeline import DetectionPipeline
from gps_modulator.fallback.fallback_manager import FallbackManager

class GeosignalValidationEngine:
    def __init__(self, detection_pipeline, fallback_manager):
        self.detection_pipeline = detection_pipeline
        self.fallback_manager = fallback_manager
        self.last_gps_point = None

    def validate(self, gps_data: Dict[str, Any], imu_data: Dict[str, Any]) -> Dict[str, Any]:
        is_spoofed = self.detection_pipeline.process_gps_point(gps_data)

        if is_spoofed: 
            # Use last known GPS position as present position for fallback
            present_position = {
                "latitude": gps_data["latitude"],
                "longitude": gps_data["longitude"]
            }
            # Calculate delta_time - assume 1.0 if no previous timestamp
            delta_time = 1.0
            if self.last_gps_point and "timestamp" in self.last_gps_point:
                delta_time = gps_data["timestamp"] - self.last_gps_point["timestamp"]
            
            validated_position = self.fallback_manager.handle_fallback(present_position, imu_data, delta_time)

            return {
                "latitude": validated_position["latitude"],
                "longitude": validated_position["longitude"],
                "is_spoofed": True,
                "source": "fallback",
                "timestamp": gps_data["timestamp"]
            }

       # If not spoofed, use GPS and update fallback state
        self.last_gps_point = {
            "latitude": gps_data["latitude"],
            "longitude": gps_data["longitude"],
            "timestamp": gps_data["timestamp"]
        }

        return {
            "latitude": gps_data["latitude"],
            "longitude": gps_data["longitude"],
            "is_spoofed": False,
            "source": "gps",
            "timestamp": gps_data["timestamp"]
        }