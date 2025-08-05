"""GPS data reader for streaming GPS coordinates."""

from typing import Dict, Any, Callable, Iterator, Optional


class GpsReader:
    """
    Reads and validates GPS data from a streaming source.
    
    This class provides a clean interface for reading GPS data from various
    sources while ensuring data validity and format consistency.
    
    Attributes:
        data_source: Callable that yields GPS data dictionaries
    """
    
    def __init__(self, data_source: Callable[[], Iterator[Dict[str, Any]]]) -> None:
        """
        Initialize the GPS reader.
        
        Args:
            data_source: A callable that returns an iterator of GPS data dictionaries.
                        Each dictionary should contain 'latitude', 'longitude', and 'timestamp'.
        """
        self.data_source = data_source
    
    def stream(self) -> Iterator[Dict[str, Any]]:
        """
        Stream valid GPS data from the data source.
        
        Yields:
            Dict[str, Any]: Validated GPS data dictionary with:
                - 'latitude' (float): Latitude in decimal degrees
                - 'longitude' (float): Longitude in decimal degrees
                - 'timestamp' (float): Unix timestamp
        """
        for gps_data in self.data_source():
            if self._is_valid(gps_data):
                yield self._normalize_data(gps_data)
    
    def _is_valid(self, gps_data: Dict[str, Any]) -> bool:
        """
        Validate GPS data structure and content.
        
        Args:
            gps_data: Dictionary to validate
        
        Returns:
            bool: True if data is valid, False otherwise
        """
        if not isinstance(gps_data, dict):
            return False
        
        try:
            # Check required keys
            required_keys = ['latitude', 'longitude', 'timestamp']
            for key in required_keys:
                if key not in gps_data:
                    # Try alternative key names
                    alt_key = 'lat' if key == 'latitude' else 'lon' if key == 'longitude' else key
                    if alt_key not in gps_data:
                        return False
            
            # Validate data types and ranges
            lat = float(gps_data.get('latitude', gps_data.get('lat', 0.0)))
            lon = float(gps_data.get('longitude', gps_data.get('lon', 0.0)))
            
            # Check coordinate ranges
            if not (-90 <= lat <= 90):
                return False
            if not (-180 <= lon <= 180):
                return False
            
            # Check timestamp
            timestamp = gps_data.get('timestamp', gps_data.get('ts'))
            if timestamp is None:
                return False
            
            float(timestamp)  # Ensure timestamp is numeric
            
            return True
            
        except (KeyError, TypeError, ValueError):
            return False
    
    def _normalize_data(self, gps_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize GPS data to consistent format.
        
        Args:
            gps_data: Raw GPS data dictionary
        
        Returns:
            Dict[str, Any]: Normalized GPS data
        """
        return {
            'latitude': float(gps_data.get('latitude', gps_data.get('lat', 0.0))),
            'longitude': float(gps_data.get('longitude', gps_data.get('lon', 0.0))),
            'timestamp': float(gps_data.get('timestamp', gps_data.get('ts', 0.0)))
        }