"""GPS-related mathematical utilities."""

import math
from datetime import datetime
from typing import Dict, Any, Union

EARTH_RADIUS = 6371000.0  # Earth's radius in meters


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    
    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees
    
    Returns:
        float: Distance between the two points in meters
    """
    # Convert to radians
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return EARTH_RADIUS * c


def compute_velocity(previous_point: Dict[str, Any], 
                    current_point: Dict[str, Any]) -> float:
    """
    Compute velocity between two GPS points.
    
    Args:
        previous_point: Previous GPS point dictionary with:
            - 'latitude' or 'lat': Latitude in decimal degrees
            - 'longitude' or 'lon': Longitude in decimal degrees
            - 'timestamp': Unix timestamp or ISO datetime string
        current_point: Current GPS point dictionary with same structure
    
    Returns:
        float: Velocity in meters per second
    """
    if previous_point is None:
        return 0.0
    
    # Extract coordinates
    prev_lat = float(previous_point.get('latitude', previous_point.get('lat', 0.0)))
    prev_lon = float(previous_point.get('longitude', previous_point.get('lon', 0.0)))
    curr_lat = float(current_point.get('latitude', current_point.get('lat', 0.0)))
    curr_lon = float(current_point.get('longitude', current_point.get('lon', 0.0)))
    
    # Extract and parse timestamps
    prev_ts = previous_point['timestamp']
    curr_ts = current_point['timestamp']
    
    time_interval = _parse_time_interval(prev_ts, curr_ts)
    
    if time_interval <= 0.0:
        return 0.0
    
    # Calculate distance
    distance = haversine_distance(prev_lat, prev_lon, curr_lat, curr_lon)
    
    return distance / time_interval


def _parse_time_interval(prev_ts: Union[str, float, int], 
                        curr_ts: Union[str, float, int]) -> float:
    """
    Parse time interval between two timestamps.
    
    Args:
        prev_ts: Previous timestamp (Unix timestamp or ISO string)
        curr_ts: Current timestamp (Unix timestamp or ISO string)
    
    Returns:
        float: Time interval in seconds
    """
    try:
        # Handle ISO format strings
        if isinstance(prev_ts, str) and isinstance(curr_ts, str):
            prev_time = datetime.fromisoformat(prev_ts.replace('Z', '+00:00'))
            curr_time = datetime.fromisoformat(curr_ts.replace('Z', '+00:00'))
            return (curr_time - prev_time).total_seconds()
        
        # Handle numeric timestamps
        return float(curr_ts) - float(prev_ts)
        
    except (ValueError, KeyError, TypeError):
        # Fallback for any parsing issues
        return 0.0


def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the bearing (direction) from point 1 to point 2.
    
    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees
    
    Returns:
        float: Bearing in degrees (0-360, where 0 is North)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon_rad = math.radians(lon2 - lon1)
    
    y = math.sin(delta_lon_rad) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon_rad))
    
    bearing_rad = math.atan2(y, x)
    bearing_deg = math.degrees(bearing_rad)
    
    # Normalize to 0-360 degrees
    return (bearing_deg + 360) % 360


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate if coordinates are within valid ranges.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees
    
    Returns:
        bool: True if coordinates are valid
    """
    return -90 <= lat <= 90 and -180 <= lon <= 180