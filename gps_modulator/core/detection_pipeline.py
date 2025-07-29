from gps_modulator.detectors.velocity_anomaly import VelocityAnomalyDetector

class DetectionPipeline:
    def __init__(self, threshold_velocity: float):
        self.velocity_anomaly_detector = VelocityAnomalyDetector(threshold_velocity)

    def process_gps_point(self, present_point: dict) -> dict:
        anomaly_detected = self.velocity_anomaly_detector.detect(present_point)
        result = {
            'velocity_anomaly': anomaly_detected,
            'point': present_point
        }
        return result