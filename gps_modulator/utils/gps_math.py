import math

EARTH_RADIUS = 6371000

def haversine(lat1, lon1, lat2, lon2):
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = EARTH_RADIUS * c
    return distance 

def compute_velocity(previous_point, present_point):
    if previous_point is None:
        return 0.0
    
    time_interval = present_point['timestamp'] - previous_point['timestamp']
    if time_interval <= 0.0:
        return 0.0
    
    # Handle both coordinate naming conventions
    prev_lat = previous_point.get('lat', previous_point.get('latitude', 0.0))
    prev_lon = previous_point.get('lon', previous_point.get('longitude', 0.0))
    curr_lat = present_point.get('lat', present_point.get('latitude', 0.0))
    curr_lon = present_point.get('lon', present_point.get('longitude', 0.0))
    
    distance = haversine(prev_lat, prev_lon, curr_lat, curr_lon)
    velocity = distance / time_interval
    return velocity

    



