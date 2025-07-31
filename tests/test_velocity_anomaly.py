from gps_modulator.detectors.velocity_anomaly import VelocityAnomalyDetector

def test_velocity_anomaly():
    print("=== Velocity Anomaly Detection Test ===\n")
    
    # Test with different threshold values
    thresholds = [10.0, 25.0, 50.0]
    
    for threshold in thresholds:
        print(f"Testing with threshold: {threshold} m/s")
        detector = VelocityAnomalyDetector(threshold_velocity=threshold)
        
        # Test cases with different movement patterns
        test_points = [
            {'lat': 19.0760, 'lon': 72.8777, 'timestamp': 1000000},  # Starting point
            {'lat': 19.0761, 'lon': 72.8780, 'timestamp': 1000005},  # Small move (normal)
            {'lat': 19.0800, 'lon': 72.8800, 'timestamp': 1000010},  # Sudden jump (likely spoof)
            {'lat': 19.0801, 'lon': 72.8802, 'timestamp': 1000015},  # Small move (normal)
            {'lat': 19.1000, 'lon': 72.9000, 'timestamp': 1000020},  # Large jump (definitely spoof)
        ]
        
        anomalies_detected = 0
        for idx, point in enumerate(test_points):
            is_anomaly = detector.detect(point)
            status = " ANOMALY" if is_anomaly else " NORMAL"
            print(f"  [{idx}] Lat: {point['lat']:.4f}, Lon: {point['lon']:.4f} → {status}")
            if is_anomaly:
                anomalies_detected += 1
        
        print(f"  Total anomalies detected: {anomalies_detected}/{len(test_points)}\n")

def test_edge_cases():
    print("=== Edge Cases Test ===\n")
    
    detector = VelocityAnomalyDetector(threshold_velocity=25.0)
    
    # Test edge cases
    edge_cases = [
        # Same point repeated
        {'lat': 19.0760, 'lon': 72.8777, 'timestamp': 1000000},
        {'lat': 19.0760, 'lon': 72.8777, 'timestamp': 1000005},  # No movement
        
        # Backwards in time (invalid)
        {'lat': 19.0761, 'lon': 72.8780, 'timestamp': 1000004},
        
        # Very small movement
        {'lat': 19.07601, 'lon': 72.87771, 'timestamp': 1000010},
    ]
    
    for idx, point in enumerate(edge_cases):
        is_anomaly = detector.detect(point)
        status = " ANOMALY" if is_anomaly else " NORMAL"
        print(f"  [{idx}] {point} → {status}")

if __name__ == "__main__":
    test_velocity_anomaly()
    test_edge_cases()
