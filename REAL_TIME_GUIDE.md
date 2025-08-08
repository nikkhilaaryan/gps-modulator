# Real-Time GPS Data Integration Guide

This guide shows you how to feed real-time GPS data into your gps-modulator project.

## Quick Overview

Your gps-modulator is designed to accept **any callable data source** that yields GPS dictionaries. You just need to replace the mock generators with real data sources.

## 1. GPS Hardware Integration

### Option A: GPSD (Linux/Unix GPS Daemon)
```python
from gps_modulator import GpsReader, VelocityAnomalyDetector, PathCorrector
import gps
import time

def gpsd_data_source():
    """Real-time GPS data from GPSD daemon"""
    try:
        session = gps.gps(mode=gps.WATCH_ENABLE)
        for report in session:
            if report['class'] == 'TPV' and hasattr(report, 'lat') and hasattr(report, 'lon'):
                yield {
                    'latitude': float(report.lat),
                    'longitude': float(report.lon),
                    'timestamp': float(report.time) if hasattr(report, 'time') else time.time(),
                    'speed': float(report.speed) if hasattr(report, 'speed') else 0.0
                }
    except Exception as e:
        print(f"GPSD connection error: {e}")

# Usage
detector = VelocityAnomalyDetector(threshold_mps=50.0)
reader = GpsReader(gpsd_data_source)
```

### Option B: Serial GPS (USB/Serial Port)
```python
import serial
import pynmea2
import time

def serial_gps_source(port='COM3', baud=9600):
    """Real-time GPS from serial/USB connection"""
    try:
        with serial.Serial(port, baud, timeout=1) as ser:
            while True:
                line = ser.readline().decode('ascii', errors='ignore').strip()
                if line.startswith('$GPGGA') or line.startswith('$GPRMC'):
                    try:
                        msg = pynmea2.parse(line)
                        if msg.latitude and msg.longitude:
                            yield {
                                'latitude': float(msg.latitude),
                                'longitude': float(msg.longitude),
                                'timestamp': time.time(),
                                'speed': float(msg.spd_over_grnd) if hasattr(msg, 'spd_over_grnd') else 0.0
                            }
                    except pynmea2.ParseError:
                        continue
    except Exception as e:
        print(f"Serial GPS error: {e}")

# Windows: Use 'COM3', 'COM4', etc.
# Linux/Mac: Use '/dev/ttyUSB0', '/dev/ttyACM0'
reader = GpsReader(lambda: serial_gps_source('COM3'))
```

### Option C: Smartphone GPS (via HTTP/API)
```python
import requests
import time

def smartphone_gps_source(api_url="http://localhost:8080/gps"):
    """Real-time GPS from smartphone app"""
    while True:
        try:
            response = requests.get(api_url, timeout=1)
            if response.status_code == 200:
                data = response.json()
                yield {
                    'latitude': float(data['lat']),
                    'longitude': float(data['lon']),
                    'timestamp': float(data.get('timestamp', time.time())),
                    'speed': float(data.get('speed', 0.0))
                }
        except Exception as e:
            print(f"Smartphone GPS error: {e}")
        time.sleep(0.5)  # 2Hz update rate

reader = GpsReader(smartphone_gps_source)
```

## 2. File-Based Real-Time Streaming

### Live CSV File Monitoring
```python
import csv
import time
import os

def csv_stream_source(filepath, update_interval=1.0):
    """Stream from continuously updated CSV file"""
    last_size = 0
    while True:
        try:
            if os.path.exists(filepath):
                current_size = os.path.getsize(filepath)
                if current_size > last_size:
                    with open(filepath, 'r') as f:
                        f.seek(last_size)
                        reader = csv.DictReader(f)
                        for row in reader:
                            yield {
                                'latitude': float(row['lat']),
                                'longitude': float(row['lon']),
                                'timestamp': float(row.get('timestamp', time.time()))
                            }
                    last_size = current_size
            time.sleep(update_interval)
        except Exception as e:
            print(f"CSV stream error: {e}")
            time.sleep(5)

reader = GpsReader(lambda: csv_stream_source('live_gps.csv'))
```

### GPX Real-Time Feed
```python
import gpxpy
import time

def gpx_stream_source(filepath, update_interval=1.0):
    """Stream from live-updated GPX file"""
    last_points = 0
    while True:
        try:
            with open(filepath, 'r') as gpx_file:
                gpx = gpxpy.parse(gpx_file)
                points = []
                for track in gpx.tracks:
                    for segment in track.segments:
                        points.extend(segment.points)
                
                if len(points) > last_points:
                    for point in points[last_points:]:
                        yield {
                            'latitude': float(point.latitude),
                            'longitude': float(point.longitude),
                            'timestamp': float(point.time.timestamp()) if point.time else time.time()
                        }
                    last_points = len(points)
            time.sleep(update_interval)
        except Exception as e:
            print(f"GPX stream error: {e}")
            time.sleep(5)

reader = GpsReader(lambda: gpx_stream_source('live_track.gpx'))
```

## 3. Complete Real-Time Example

```python
# real_time_detector.py
from gps_modulator import GpsReader, VelocityAnomalyDetector, PathCorrector, LivePathPlotter
import argparse
import logging

def create_real_gps_source(source_type='mock', **kwargs):
    """Factory function for different GPS sources"""
    
    if source_type == 'mock':
        from gps_modulator.streaming import MockGpsGenerator
        generator = MockGpsGenerator(**kwargs)
        return generator.generate
    
    elif source_type == 'gpsd':
        return gpsd_data_source
    
    elif source_type == 'serial':
        port = kwargs.get('port', 'COM3')
        baud = kwargs.get('baud', 9600)
        return lambda: serial_gps_source(port, baud)
    
    elif source_type == 'csv':
        filepath = kwargs.get('filepath', 'live_gps.csv')
        return lambda: csv_stream_source(filepath)
    
    else:
        raise ValueError(f"Unknown source type: {source_type}")

def main():
    parser = argparse.ArgumentParser(description='Real-time GPS spoofing detection')
    parser.add_argument('--source', choices=['mock', 'gpsd', 'serial', 'csv'], default='mock')
    parser.add_argument('--port', default='COM3', help='Serial port for GPS')
    parser.add_argument('--file', default='live_gps.csv', help='CSV file path')
    parser.add_argument('--threshold', type=float, default=50.0, help='Velocity threshold')
    
    args = parser.parse_args()
    
    # Create data source
    gps_source = create_real_gps_source(
        source_type=args.source,
        port=args.port,
        filepath=args.file
    )
    
    # Initialize components
    detector = VelocityAnomalyDetector(threshold_mps=args.threshold)
    corrector = PathCorrector()
    reader = GpsReader(gps_source)
    plotter = LivePathPlotter(max_points=1000)
    
    # Run detection
    previous_point = None
    for point in reader.stream():
        detector.previous_point = previous_point
        is_spoofed = detector.detect(previous_point, point)
        
        if is_spoofed:
            corrected_point = corrector.correct(previous_point, point, is_spoofed=True)
            print(f"Spoofing detected! Corrected: {corrected_point}")
        else:
            corrected_point = point
        
        # Update visualization
        plotter.add_point(point, corrected_point, is_spoofed)
        
        previous_point = point

if __name__ == "__main__":
    main()
```

## 4. Usage Examples

### Run with different sources:
```bash
# Mock data (default)
python real_time_detector.py --source mock

# GPSD (Linux)
python real_time_detector.py --source gpsd

# Serial GPS on Windows
python real_time_detector.py --source serial --port COM3

# Serial GPS on Linux
python real_time_detector.py --source serial --port /dev/ttyUSB0

# CSV file streaming
python real_time_detector.py --source csv --file live_gps.csv
```

## 5. Hardware Requirements

### GPS Modules Tested:
- **u-blox NEO-6M** (Serial/USB)
- **GlobalSat BU-353S4** (USB)
- **Adafruit Ultimate GPS** (Serial/I2C)
- **Smartphone GPS** (via WiFi/API)

### Connection Types:
- **USB**: Plug-and-play with serial drivers
- **Serial**: RX/TX pins or USB-to-serial adapter
- **Bluetooth**: Virtual COM port
- **WiFi**: HTTP API endpoints

## 6. Troubleshooting

### Common Issues:
1. **Permission denied**: Run as administrator or add user to dialout group
2. **Port not found**: Check device manager for correct COM port
3. **No GPS lock**: Ensure clear sky view and wait 30-60 seconds
4. **Data format errors**: Check NMEA sentence compatibility

### Windows Serial Port Detection:
```python
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"Port: {port.device}, Description: {port.description}")
```

### Testing GPS Connection:
```python
import serial
ser = serial.Serial('COM3', 9600, timeout=1)
while True:
    line = ser.readline().decode('ascii', errors='ignore')
    if '$GPGGA' in line:
        print("GPS responding:", line.strip())
```

Your gps-modulator is ready for real-time GPS data! Just choose the integration method that matches your hardware setup.