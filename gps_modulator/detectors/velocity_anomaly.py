from gps_modulator.utils.gps_math import compute_velocity

class VelocityAnomalyDetector:
    def __init__(self, threshold_velocity: float):
        self.threshold_velocity = threshold_velocity
        self.previous_point = None

    def detect(self, present_point):
        if self.previous_point is None:
            self.previous_point = present_point
            return False

        velocity = compute_velocity(self.previous_point, present_point)
        self.previous_point = present_point
        if velocity > self.threshold_velocity:
            return True
        return False
    