import pytest
import math
from gps_modulator.fallback.dead_reckoner import DeadReckoner

class TestDeadReckoner:
    
    def test_basic_movement(self):
        """Test basic dead reckoning with acceleration and heading."""
        initial_position = {'latitude': 19.0760, 'longitude': 72.8777}
        initial_velocity = 5.0  # m/s
        
        reckoner = DeadReckoner(initial_position, initial_velocity)
        
        imu_data = {
            'acceleration': 0.5,  # m/s²
            'heading': 90         # degrees (East)
        }
        delta_time = 15.0  # seconds
        
        next_position = reckoner.update(imu_data, delta_time)
        
        # Check that position moved eastward
        assert next_position['latitude'] == pytest.approx(19.0760, rel=1e-5)
        assert next_position['longitude'] > 72.8777
        assert next_position['longitude'] == pytest.approx(72.87948, rel=1e-5)
    
    def test_velocity_update(self):
        """Test that velocity increases with acceleration."""
        initial_position = {'latitude': 0.0, 'longitude': 0.0}
        initial_velocity = 10.0  # m/s
        
        reckoner = DeadReckoner(initial_position, initial_velocity)
        
        # First update
        imu_data = {'acceleration': 2.0, 'heading': 0}  # North
        delta_time = 5.0
        
        # Velocity should increase: 10 + (2 * 5) = 20 m/s
        # Distance: 15 * 5 = 75m (average velocity during acceleration)
        reckoner.update(imu_data, delta_time)
        
        # Second update with same acceleration
        next_position = reckoner.update(imu_data, delta_time)
        
        # Should have moved further north
        assert next_position['latitude'] > 0.0
        assert next_position['longitude'] == pytest.approx(0.0, rel=1e-10)
    
    def test_velocity_only_mode(self):
        """Test dead reckoning with velocity data (no acceleration)."""
        initial_position = {'latitude': 19.0760, 'longitude': 72.8777}
        initial_velocity = 10.0  # m/s
        
        reckoner = DeadReckoner(initial_position, initial_velocity)
        
        # Test with velocity-only IMU data
        imu_data = {
            'velocity': 15.0,  # Use provided velocity instead of acceleration
            'heading': 45      # Northeast
        }
        delta_time = 10.0
        
        next_position = reckoner.update(imu_data, delta_time)
        
        # Should have moved northeast
        assert next_position['latitude'] > 19.0760
        assert next_position['longitude'] > 72.8777
    
    def test_stationary_case(self):
        """Test behavior when no movement occurs."""
        initial_position = {'latitude': 19.0760, 'longitude': 72.8777}
        initial_velocity = 0.0
        
        reckoner = DeadReckoner(initial_position, initial_velocity)
        
        imu_data = {'acceleration': 0.0, 'heading': 0}
        delta_time = 10.0
        
        next_position = reckoner.update(imu_data, delta_time)
        
        # Position should remain unchanged
        assert next_position['latitude'] == pytest.approx(19.0760)
        assert next_position['longitude'] == pytest.approx(72.8777)
    
    def test_heading_effects(self):
        """Test movement in different cardinal directions."""
        initial_position = {'latitude': 0.0, 'longitude': 0.0}
        initial_velocity = 5.0
        
        test_cases = [
            (0, "North", lambda lat, lon: lat > 0 and abs(lon) < 1e-10),
            (90, "East", lambda lat, lon: abs(lat) < 1e-10 and lon > 0),
            (180, "South", lambda lat, lon: lat < 0 and abs(lon) < 1e-10),
            (270, "West", lambda lat, lon: abs(lat) < 1e-10 and lon < 0),
        ]
        
        for heading, direction, check_func in test_cases:
            reckoner = DeadReckoner(initial_position, initial_velocity)
            imu_data = {'acceleration': 0.0, 'heading': heading}
            
            next_position = reckoner.update(imu_data, 1.0)
            
            assert check_func(next_position['latitude'], next_position['longitude']), \
                f"Failed movement test for {direction} direction"
    
    def test_zero_delta_time(self):
        """Test edge case with zero time interval."""
        initial_position = {'latitude': 19.0760, 'longitude': 72.8777}
        initial_velocity = 10.0
        
        reckoner = DeadReckoner(initial_position, initial_velocity)
        
        imu_data = {'acceleration': 5.0, 'heading': 90}
        delta_time = 0.0
        
        next_position = reckoner.update(imu_data, delta_time)
        
        # Position should not change with zero time
        assert next_position['latitude'] == pytest.approx(19.0760)
        assert next_position['longitude'] == pytest.approx(72.8777)

def run_demo():
    """Interactive demo function for manual testing."""
    print("=== Dead Reckoner Demo ===\n")
    
    # Mumbai coordinates demo
    initial_position = {'latitude': 19.0760, 'longitude': 72.8777}
    initial_velocity = 5.0
    
    reckoner = DeadReckoner(initial_position, initial_velocity)
    
    scenarios = [
        {"name": "Accelerating East", "imu": {"acceleration": 1.0, "heading": 90}, "time": 10},
        {"name": "Constant North", "imu": {"acceleration": 0.0, "heading": 0}, "time": 5},
        {"name": "Decelerating South", "imu": {"acceleration": -0.5, "heading": 180}, "time": 8},
    ]
    
    for scenario in scenarios:
        print(f"Scenario: {scenario['name']}")
        print(f"Initial: {initial_position}, Velocity: {initial_velocity} m/s")
        
        next_pos = reckoner.update(scenario['imu'], scenario['time'])
        
        print(f"After {scenario['time']}s: {next_pos}")
        print(f"Distance moved: ~{((next_pos['latitude']-initial_position['latitude'])**2 + (next_pos['longitude']-initial_position['longitude'])**2)**0.5 * 111000:.1f} km")
        print()

if __name__ == "__main__":
    # Run pytest tests
    pytest.main([__file__, "-v"])
    
    # Run interactive demo
    print("\n" + "="*50)
    run_demo()
