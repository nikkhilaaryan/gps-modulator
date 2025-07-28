from gps_modulator.fallback.fallback_manager import FallbackManager

def test_handle_fallback_activation():
    manager = FallbackManager()

    gps_point = {'lat': 19.0760, 'lon': 72.8777}
    imu_data = {
        'acceleration': 0.5,
        'heading': 90.0,
        'velocity': 5.0
    }
    delta_time = 2.0

    # Trigger fallback
    estimated_position = manager.handle_fallback(gps_point, imu_data, delta_time)

    assert manager.is_fallback_active() is True
    assert isinstance(estimated_position, dict)
    assert 'lat' in estimated_position and 'lon' in estimated_position
    assert estimated_position['lon'] > gps_point['lon']  # eastward heading → longitude increases

def test_handle_gps_restored():
    manager = FallbackManager()

    gps_point = {'lat': 19.0760, 'lon': 72.8777}
    imu_data = {
        'acceleration': 0.2,
        'heading': 180.0,
        'velocity': 3.0
    }

    manager.handle_fallback(gps_point, imu_data, 2.0)

    assert manager.is_fallback_active() is True

    restored_gps = {'lat': 19.0755, 'lon': 72.8775}
    manager.handle_gps_restored(restored_gps)

    assert manager.is_fallback_active() is False
    assert manager.last_position == restored_gps

   
