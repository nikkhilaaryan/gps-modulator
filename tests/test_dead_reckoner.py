import pytest
from gps_modulator.fallback.dead_reckoner import DeadReckoner

def test_dead_reckoner():
    initial_position = {'lat': 19.0760, 'lon': 72.8777}  # Mumbai
    initial_velocity = 5.0  # meters per second
    reckoner = DeadReckoner(initial_position, initial_velocity)
    imu_data = {
        'acceleration': 0.5,     # m/s²
        'heading': 90            # degrees (East)
    }
    delta_time = 15  # seconds  # Corrected to match the print statement
    next_position = reckoner.update(imu_data, delta_time)
    # Assertions based on expected output
    assert next_position['lat'] == 19.076
    assert next_position['lon'] == pytest.approx(72.87948420609372)

# Remove or comment out the print for proper testing
# print("Estimated Position after 15s:", next_position)
