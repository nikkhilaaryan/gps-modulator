from gps_modulator.core.detection_pipeline import detection_pipeline

pipeline = detection_pipeline(threshold_velocity=25.0)

gps_points = [
    {'lat': 19.0760, 'lon': 72.8777, 'timestamp': 1000000},  # Mumbai
    {'lat': 19.0761, 'lon': 72.8780, 'timestamp': 1000005},  # Small move
    {'lat': 19.0800, 'lon': 72.8800, 'timestamp': 1000010},  # Sudden jump (possible spoof)
    {'lat': 19.0801, 'lon': 72.8802, 'timestamp': 1000015},  # Normal again
]

for idx, point in enumerate(gps_points):
    result = pipeline.process_gps_point(point)
    print(f"[{idx}] GPS Point: {point} → Anomaly Detected: {result['velocity_anomaly']}")
