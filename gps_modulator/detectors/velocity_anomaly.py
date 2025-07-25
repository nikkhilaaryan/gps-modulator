from gps_modulator.utils.gps_math import compute_velocity

class velocity_anomaly_detector:
    def __init__(self, threshold_velocity: float):
        self.threshold_velocity = threshold_velocity
        self.past_point = None

    def detect(self, present_point):
        if self.past_point is None:
            self.past_point = present_point
            return False

        velocity = compute_velocity(self.past_point, present_point)
        self.past_point = present_point
        if velocity > self.threshold_velocity:
            return True
        return False