import time
import logging
import os
import math
import random
import csv
from typing import Dict, Any, Iterator, Optional
from abc import ABC, abstractmethod

# Optional dependencies - only import when needed
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import pynmea2
    NMEA_AVAILABLE = True
except ImportError:
    NMEA_AVAILABLE = False

try:
    import requests
    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False


class RealTimeSource(ABC):
    """Abstract base class for real-time GPS data sources."""
    
    @abstractmethod
    def stream(self) -> Iterator[Dict[str, Any]]:
        """Stream GPS data points."""
        pass
    
    @abstractmethod
    def start(self) -> None:
        """Start the GPS source."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop the GPS source."""
        pass


class SerialGPSSource(RealTimeSource):
    """Real-time GPS data from serial/USB connection."""
    
    def __init__(self, port: str, baud_rate: int = 9600, timeout: float = 1.0):
        """
        Initialize serial GPS source.
        
        Args:
            port: Serial port (e.g., 'COM3', '/dev/ttyUSB0')
            baud_rate: Baud rate (default: 9600)
            timeout: Read timeout in seconds
        """
        if not SERIAL_AVAILABLE:
            raise ImportError("pyserial is required. Install with: pip install pyserial")
        if not NMEA_AVAILABLE:
            raise ImportError("pynmea2 is required. Install with: pip install pynmea2")
            
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial_connection = None
        self.logger = logging.getLogger(__name__)
        
    def start(self) -> None:
        """Start the serial GPS connection."""
        try:
            self.serial_connection = serial.Serial(
                self.port, 
                self.baud_rate, 
                timeout=self.timeout
            )
            self.logger.info(f"GPS connected to {self.port} at {self.baud_rate} baud")
        except Exception as e:
            self.logger.error(f"Failed to connect to GPS: {e}")
            raise
    
    def stream(self) -> Iterator[Dict[str, Any]]:
        """Stream GPS data from serial connection."""
        if not self.serial_connection:
            self.start()
            
        while True:
            try:
                line = self.serial_connection.readline().decode('ascii', errors='ignore').strip()
                if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                    msg = pynmea2.parse(line)
                    if msg.latitude and msg.longitude:
                        yield {
                            'latitude': float(msg.latitude),
                            'longitude': float(msg.longitude),
                            'timestamp': time.time(),
                            'speed': float(msg.spd_over_grnd) if hasattr(msg, 'spd_over_grnd') else 0.0,
                            'altitude': float(msg.altitude) if hasattr(msg, 'altitude') else 0.0
                        }
            except Exception as e:
                self.logger.warning(f"GPS parsing error: {e}")
                time.sleep(1)
    
    def stop(self) -> None:
        """Close the serial connection."""
        if self.serial_connection:
            self.serial_connection.close()
            self.logger.info("GPS serial connection closed")


class HttpGPSSource(RealTimeSource):
    """Real-time GPS data from HTTP API."""
    
    def __init__(self, api_url: str, update_interval: float = 1.0):
        """
        Initialize HTTP GPS source.
        
        Args:
            api_url: HTTP endpoint URL
            update_interval: Update interval in seconds
        """
        if not HTTP_AVAILABLE:
            raise ImportError("requests is required. Install with: pip install requests")
            
        self.api_url = api_url
        self.update_interval = update_interval
        self.logger = logging.getLogger(__name__)
    
    def start(self) -> None:
        """Test the HTTP connection."""
        try:
            response = requests.get(self.api_url, timeout=5)
            if response.status_code != 200:
                raise ConnectionError(f"HTTP error {response.status_code}")
            self.logger.info(f"HTTP GPS source connected to {self.api_url}")
        except Exception as e:
            self.logger.error(f"Failed to connect to HTTP GPS: {e}")
            raise
    
    def stream(self) -> Iterator[Dict[str, Any]]:
        """Stream GPS data from HTTP API."""
        while True:
            try:
                response = requests.get(self.api_url, timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    yield {
                        'latitude': float(data['lat']),
                        'longitude': float(data['lon']),
                        'timestamp': float(data.get('timestamp', time.time())),
                        'speed': float(data.get('speed', 0.0)),
                        'accuracy': float(data.get('accuracy', 0.0))
                    }
            except Exception as e:
                self.logger.warning(f"HTTP GPS error: {e}")
            time.sleep(self.update_interval)
    
    def stop(self) -> None:
        """No cleanup needed for HTTP."""
        pass


class FileGPSSource(RealTimeSource):
    """Real-time GPS data from continuously updated file."""
    
    def __init__(self, filepath: str, update_interval: float = 1.0):
        """
        Initialize file-based GPS source.
        
        Args:
            filepath: Path to CSV or GPX file
            update_interval: Check interval in seconds
        """
        self.filepath = filepath
        self.update_interval = update_interval
        self.last_size = 0
        self.last_position = 0
        self.logger = logging.getLogger(__name__)
    
    def start(self) -> None:
        """Initialize file monitoring."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"GPS file not found: {self.filepath}")
        self.logger.info(f"File GPS source monitoring {self.filepath}")
    
    def stream(self) -> Iterator[Dict[str, Any]]:
        """Stream GPS data from file."""
        
        if not os.path.exists(self.filepath):
            self.logger.error(f"File not found: {self.filepath}")
            return # Exit if file doesn't exist

        try:
            with open(self.filepath, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield {
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude']),
                        'altitude': float(row.get('altitude', 0.0)),
                        'timestamp': float(row.get('timestamp', time.time()))
                    }
        except Exception as e:
            self.logger.error(f"Error reading from file {self.filepath}: {e}")

    def stop(self) -> None:
        """No specific cleanup needed for file source."""
        pass


class MockGpsGenerator(RealTimeSource):
    """Generates mock GPS data for testing and demonstration."""

    def __init__(
        self,
        start_lat: float = 34.0522,
        start_lon: float = -118.2437,
        velocity_mps: float = 1.0,
        spoof_rate: float = 0.05,
        spoof_magnitude: float = 0.0001,
        update_interval: float = 1.0
    ):
        """
        Initialize the mock GPS generator.

        Args:
            start_lat: Starting latitude.
            start_lon: Starting longitude.
            velocity_mps: Simulated velocity in meters per second.
            spoof_rate: Probability of a spoofing event (0.0 to 1.0).
            spoof_magnitude: Magnitude of the spoofing jump in degrees.
            update_interval: Time interval between generated points in seconds.
        """
        self.current_lat = start_lat
        self.current_lon = start_lon
        self.velocity_mps = velocity_mps
        self.spoof_rate = spoof_rate
        self.spoof_magnitude = spoof_magnitude
        self.update_interval = update_interval
        self.logger = logging.getLogger(__name__)

    def start(self) -> None:
        """No specific start action for mock generator."""
        self.logger.info("Mock GPS generator started.")

    def stream(self) -> Iterator[Dict[str, Any]]:
        """Stream mock GPS data points."""
        while True:
            # Simulate movement (simple linear progression for demonstration)
            # 1 degree of latitude is approx 111,320 meters
            # 1 degree of longitude is approx 111,320 * cos(latitude) meters
            delta_lat = (self.velocity_mps * self.update_interval) / 111320.0
            delta_lon = (self.velocity_mps * self.update_interval) / (111320.0 * abs(math.cos(math.radians(self.current_lat))))

            self.current_lat += delta_lat
            self.current_lon += delta_lon

            # Simulate spoofing
            is_spoofed = False
            if random.random() < self.spoof_rate:
                self.current_lat += random.uniform(-self.spoof_magnitude, self.spoof_magnitude)
                self.current_lon += random.uniform(-self.spoof_magnitude, self.spoof_magnitude)
                is_spoofed = True
                self.logger.debug("Simulating spoofing event.")

            point = {
                'latitude': self.current_lat,
                'longitude': self.current_lon,
                'altitude': 100.0,  # Static altitude for mock data
                'timestamp': time.time(),
                'speed': self.velocity_mps,
                'is_spoofed_simulated': is_spoofed # For internal mock data tracking
            }
            yield point
            time.sleep(self.update_interval)

    def stop(self) -> None:
        """No specific stop action for mock generator."""
        self.logger.info("Mock GPS generator stopped.")


def create_gps_source(
    source_type: str,
    file_path: Optional[str] = None,
    port: Optional[str] = None,
    baud_rate: int = 9600,
    url: Optional[str] = None
) -> RealTimeSource:
    """
    Factory function to create a GPS data source based on type.

    Args:
        source_type: Type of GPS data source ('mock', 'file', 'serial', 'http').
        file_path: Path to input file for 'file' source type.
        port: Serial port for 'serial' source type.
        baud_rate: Baud rate for 'serial' source type.
        url: URL for 'http' source type.

    Returns:
        An instance of a RealTimeSource subclass.

    Raises:
        ValueError: If an invalid source_type is provided or required arguments are missing.
    """
    if source_type == 'mock':
        return MockGpsGenerator()
    elif source_type == 'file':
        if not file_path:
            raise ValueError("file_path is required for 'file' source type.")
        return FileGPSSource(file_path)
    elif source_type == 'serial':
        if not port:
            raise ValueError("port is required for 'serial' source type.")
        return SerialGPSSource(port, baud_rate)
    elif source_type == 'http':
        if not url:
            raise ValueError("url is required for 'http' source type.")
        return HttpGPSSource(url)
    else:
        raise ValueError(f"Unknown source type: {source_type}")


# Convenience functions for direct usage
def get_serial_gps_source(port: str, baud: int = 9600):
    """Get serial GPS data source."""
    source = SerialGPSSource(port, baud)
    return source.stream

def get_http_gps_source(url: str, interval: float = 1.0):
    """Get HTTP GPS data source."""
    source = HttpGPSSource(url, interval)
    return source.stream

def get_file_gps_source(filepath: str, interval: float = 1.0):
    """Get file-based GPS data source."""
    source = FileGPSSource(filepath, interval)
    return source.stream


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example 1: Serial GPS
    # gps_source = get_serial_gps_source('COM3', 9600)
    
    # Example 2: HTTP GPS
    # gps_source = get_http_gps_source('http://localhost:8080/gps')
    
    # Example 3: File GPS
    # gps_source = get_file_gps_source('live_gps.csv')
    
    print("Real-time GPS sources ready for integration!")