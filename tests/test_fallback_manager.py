import pytest
from gps_modulator.fallback.fallback_manager import FallbackManager

class TestFallbackManager:
    
    def test_initial_state(self):
        """Test that FallbackManager starts in correct initial state."""
        manager = FallbackManager()
        
        assert manager.is_fallback_active() is False
        assert manager.last_position is None
    
    def test_fallback_activation(self):
        """Test fallback activation with proper position estimation."""
        manager = FallbackManager()
        
        gps_point = {'latitude': 19.0760, 'longitude': 72.8777}
        imu_data = {
            'acceleration': 0.5,
            'heading': 90.0,
            'velocity': 5.0
        }
        delta_time = 2.0
        
        # First fallback call should activate fallback
        estimated_position = manager.handle_fallback(gps_point, imu_data, delta_time)
        
        assert manager.is_fallback_active() is True
        assert isinstance(estimated_position, dict)
        assert 'latitude' in estimated_position and 'longitude' in estimated_position
        assert estimated_position['longitude'] > gps_point['longitude']  # eastward movement
        assert estimated_position['latitude'] == pytest.approx(19.0760, rel=1e-5)
    
    def test_continuous_fallback_mode(self):
        """Test fallback continues when already active."""
        manager = FallbackManager()
        
        # Initial position
        initial_pos = {'latitude': 19.0760, 'longitude': 72.8777}
        
        # First fallback call
        imu_data1 = {'acceleration': 1.0, 'heading': 45.0, 'velocity': 5.0}
        pos1 = manager.handle_fallback(initial_pos, imu_data1, 3.0)
        
        assert manager.is_fallback_active() is True
        
        # Second fallback call (should continue with dead reckoning)
        imu_data2 = {'acceleration': 0.0, 'heading': 90.0, 'velocity': 8.0}
        pos2 = manager.handle_fallback(pos1, imu_data2, 2.0)
        
        assert manager.is_fallback_active() is True
        assert pos2 != pos1  # Position should have changed
        assert pos2['longitude'] > pos1['longitude']
    
    def test_gps_restoration(self):
        """Test GPS restoration after fallback."""
        manager = FallbackManager()
        
        # Start with fallback
        gps_point = {'latitude': 19.0760, 'longitude': 72.8777}
        imu_data = {'acceleration': 0.2, 'heading': 180.0, 'velocity': 3.0}
        
        manager.handle_fallback(gps_point, imu_data, 2.0)
        assert manager.is_fallback_active() is True
        
        # Restore GPS
        restored_gps = {'latitude': 19.0755, 'longitude': 72.8775}
        manager.handle_gps_restored(restored_gps)
        
        assert manager.is_fallback_active() is False
        assert manager.last_position == restored_gps
    
    def test_velocity_handling(self):
        """Test velocity updates during fallback."""
        manager = FallbackManager()
        
        gps_point = {'latitude': 0.0, 'longitude': 0.0}
        
        # Test with acceleration-based velocity
        imu_data = {'acceleration': 2.0, 'heading': 0.0, 'velocity': 10.0}
        
        pos1 = manager.handle_fallback(gps_point, imu_data, 5.0)
        
        # Should have moved north
        assert pos1['latitude'] > 0.0
        assert pos1['longitude'] == pytest.approx(0.0, abs=1e-10)
    
    def test_zero_movement_fallback(self):
        """Test fallback with zero movement parameters."""
        manager = FallbackManager()
        
        gps_point = {'latitude': 19.0760, 'longitude': 72.8777}
        imu_data = {'acceleration': 0.0, 'heading': 0.0, 'velocity': 0.0}
        
        estimated_position = manager.handle_fallback(gps_point, imu_data, 10.0)
        
        assert manager.is_fallback_active() is True
        # Position should remain same with zero movement
        assert estimated_position['latitude'] == pytest.approx(19.0760)
        assert estimated_position['longitude'] == pytest.approx(72.8777)
    
    def test_coordinate_key_handling(self):
        """Test handling of different coordinate key formats."""
        manager = FallbackManager()
        
        # Test with 'lat'/'lon' format (should be handled)
        gps_point = {'lat': 19.0760, 'lon': 72.8777}
        imu_data = {'acceleration': 0.5, 'heading': 90.0, 'velocity': 5.0}
        
        estimated_position = manager.handle_fallback(gps_point, imu_data, 2.0)
        
        assert manager.is_fallback_active() is True
        assert isinstance(estimated_position, dict)
        assert 'latitude' in estimated_position or 'lat' in estimated_position
    
    def test_multiple_fallback_cycles(self):
        """Test multiple fallback cycles with GPS restoration."""
        manager = FallbackManager()
        
        # Cycle 1: Start fallback
        gps1 = {'latitude': 19.0760, 'longitude': 72.8777}
        imu1 = {'acceleration': 1.0, 'heading': 45.0, 'velocity': 10.0}
        
        pos1 = manager.handle_fallback(gps1, imu1, 3.0)
        assert manager.is_fallback_active() is True
        
        # Continue fallback
        imu2 = {'acceleration': 0.5, 'heading': 90.0, 'velocity': 12.0}
        pos2 = manager.handle_fallback(pos1, imu2, 2.0)
        
        # Restore GPS
        restored_gps = {'latitude': 19.078, 'longitude': 72.880}
        manager.handle_gps_restored(restored_gps)
        assert manager.is_fallback_active() is False
        
        # Start new fallback cycle
        imu3 = {'acceleration': 0.0, 'heading': 180.0, 'velocity': 5.0}
        pos3 = manager.handle_fallback(restored_gps, imu3, 4.0)
        
        assert manager.is_fallback_active() is True
        assert pos3['latitude'] < restored_gps['latitude']  # moved south

def run_demo():
    """Interactive demo for testing fallback scenarios."""
    print("=== Fallback Manager Demo ===\n")
    
    manager = FallbackManager()
    
    scenarios = [
        {
            "name": "GPS Signal Lost - Start Fallback",
            "gps": {'latitude': 19.0760, 'longitude': 72.8777},
            "imu": {'acceleration': 1.0, 'heading': 90.0, 'velocity': 8.0},
            "time": 3.0
        },
        {
            "name": "Continue in Fallback Mode",
            "gps": None,  # No GPS, use previous position
            "imu": {'acceleration': 0.5, 'heading': 45.0, 'velocity': 10.0},
            "time": 2.0
        },
        {
            "name": "GPS Restored",
            "gps": {'latitude': 19.077, 'longitude': 72.88},
            "imu": None,
            "time": None
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"Step {i}: {scenario['name']}")
        
        if scenario['gps'] and scenario['imu']:
            # Start fallback
            pos = manager.handle_fallback(
                scenario['gps'], scenario['imu'], scenario['time']
            )
            print(f"  Fallback activated: {manager.is_fallback_active()}")
            print(f"  Estimated position: {pos}")
            
        elif scenario['imu']:
            # Continue fallback
            last_pos = manager.last_position
            pos = manager.handle_fallback(
                last_pos, scenario['imu'], scenario['time']
            )
            print(f"  Still in fallback: {manager.is_fallback_active()}")
            print(f"  New estimated position: {pos}")
            
        else:
            # Restore GPS
            manager.handle_gps_restored(scenario['gps'])
            print(f"  GPS restored, fallback active: {manager.is_fallback_active()}")
            print(f"  Current position: {manager.last_position}")
        
        print()

if __name__ == "__main__":
    # Run pytest tests
    pytest.main([__file__, "-v"])
    
    # Run interactive demo
    print("\n" + "="*50)
    run_demo()

   
