from gps_modulator.core.geosignal_validation_engine import GeosignalValidationEngine
from gps_modulator.core.detection_pipeline import DetectionPipeline
from gps_modulator.fallback.fallback_manager import FallbackManager

def mock_data_stream():
    # Normal points
    yield {"latitude": 20.0, "longitude": 85.0, "timestamp": 1.0}, {"velocity": 0.5, "heading": 90, "timestamp": 1.0}
    yield {"latitude": 20.0001, "longitude": 85.0001, "timestamp": 2.0}, {"velocity": 0.6, "heading": 90, "timestamp": 2.0}
    
    # Spoofed point (sudden jump)
    yield {"latitude": 20.5, "longitude": 85.5, "timestamp": 3.0}, {"velocity": 0.7, "heading": 90, "timestamp": 3.0}
    
    # Back to normal
    yield {"latitude": 20.0002, "longitude": 85.0002, "timestamp": 4.0}, {"velocity": 0.5, "heading": 90, "timestamp": 4.0}

def main():
    detection_pipeline = DetectionPipeline(threshold_velocity=50.0)
    fallback_manager = FallbackManager()

    engine = GeosignalValidationEngine(detection_pipeline, fallback_manager)

    print("=== Running GeoSignal Validation Demo ===\n")
    for gps_data, imu_data in mock_data_stream():
        result = engine.validate(gps_data, imu_data)
        print(f"[Time {result['timestamp']:.1f}] Source: {result['source'].upper()} | "
              f"Lat: {result['latitude']:.6f}, Lon: {result['longitude']:.6f} | "
              f"Spoofed: {result['is_spoofed']}")

if __name__ == "__main__":
    main()