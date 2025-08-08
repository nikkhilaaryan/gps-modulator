"""
Real-Time GPS Spoofing Detection with Hardware Integration

This example demonstrates how to use real GPS hardware with your gps-modulator.
It supports multiple data sources: serial GPS, HTTP API, file streaming, etc.
"""

import argparse
import logging
import sys
import os

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gps_modulator import (
    GpsReader, 
    VelocityAnomalyDetector, 
    PathCorrector, 
    LivePathPlotter
)

# Import real-time sources
try:
    from gps_modulator.streaming.real_time_sources import (
        get_serial_gps_source,
        get_http_gps_source,
        get_file_gps_source,
        GPSSourceFactory
    )
    REAL_TIME_AVAILABLE = True
except ImportError as e:
    print(f"Real-time sources not available: {e}")
    print("Install dependencies: pip install pyserial pynmea2 requests")
    REAL_TIME_AVAILABLE = False


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def detect_available_ports():
    """Auto-detect available GPS ports."""
    try:
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        gps_ports = []
        
        for port in ports:
            # Common GPS device descriptions
            gps_keywords = ['GPS', 'u-blox', 'Prolific', 'FTDI', 'CH340']
            if any(keyword in port.description.upper() for keyword in gps_keywords):
                gps_ports.append(port.device)
        
        return gps_ports
    except ImportError:
        return []


def create_gps_source(args):
    """Create GPS data source based on arguments."""
    logger = logging.getLogger(__name__)
    
    if args.source == 'mock':
        from gps_modulator.streaming import MockGpsGenerator
        generator = MockGpsGenerator(
            start_lat=args.start_lat,
            start_lon=args.start_lon,
            velocity_mps=args.velocity,
            spoof_rate=args.spoof_rate
        )
        logger.info("Using mock GPS data for testing")
        return generator.generate
    
    elif args.source == 'serial':
        if not REAL_TIME_AVAILABLE:
            raise RuntimeError("Real-time sources not available")
        
        if not args.port:
            available_ports = detect_available_ports()
            if available_ports:
                args.port = available_ports[0]
                logger.info(f"Auto-detected GPS port: {args.port}")
            else:
                raise ValueError("No GPS port specified and none auto-detected")
        
        logger.info(f"Using serial GPS on {args.port} at {args.baud} baud")
        return get_serial_gps_source(args.port, args.baud)
    
    elif args.source == 'http':
        if not REAL_TIME_AVAILABLE:
            raise RuntimeError("Real-time sources not available")
        
        logger.info(f"Using HTTP GPS from {args.url}")
        return get_http_gps_source(args.url, args.interval)
    
    elif args.source == 'file':
        if not REAL_TIME_AVAILABLE:
            raise RuntimeError("Real-time sources not available")
        
        if not os.path.exists(args.filepath):
            # Create sample file for testing
            create_sample_gps_file(args.filepath)
        
        logger.info(f"Using file GPS from {args.filepath}")
        return get_file_gps_source(args.filepath, args.interval)
    
    else:
        raise ValueError(f"Unknown source type: {args.source}")


def create_sample_gps_file(filepath: str):
    """Create a sample GPS file for testing."""
    import csv
    
    print(f"Creating sample GPS file: {filepath}")
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['lat', 'lon', 'timestamp'])
        
        # Generate some sample points
        base_lat, base_lon = 37.7749, -122.4194  # San Francisco
        for i in range(100):
            lat = base_lat + (i * 0.0001)
            lon = base_lon + (i * 0.0001)
            writer.writerow([lat, lon, time.time() + i])


def main():
    """Main real-time GPS spoofing detection system."""
    parser = argparse.ArgumentParser(
        description='Real-time GPS spoofing detection with hardware integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python real_time_demo.py --source mock
  python real_time_demo.py --source serial --port COM3
  python real_time_demo.py --source http --url http://localhost:8080/gps
  python real_time_demo.py --source file --filepath live_gps.csv
  
Hardware Setup:
  - Connect GPS to USB/serial port
  - Install drivers if needed
  - Ensure clear sky view for GPS lock
        """
    )
    
    # Source selection
    parser.add_argument(
        '--source',
        choices=['mock', 'serial', 'http', 'file'],
        default='mock',
        help='GPS data source type'
    )
    
    # Serial GPS options
    parser.add_argument('--port', help='Serial port (e.g., COM3, /dev/ttyUSB0)')
    parser.add_argument('--baud', type=int, default=9600, help='Baud rate (default: 9600)')
    
    # HTTP GPS options
    parser.add_argument('--url', default='http://localhost:8080/gps', help='HTTP API URL')
    
    # File GPS options
    parser.add_argument('--filepath', default='live_gps.csv', help='GPS data file path')
    
    # Common options
    parser.add_argument('--interval', type=float, default=1.0, help='Update interval (seconds)')
    parser.add_argument('--threshold', type=float, default=50.0, help='Velocity threshold (m/s)')
    parser.add_argument('--max-points', type=int, default=1000, help='Max points to display')
    parser.add_argument('--no-plot', action='store_true', help='Disable live plotting')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    # Mock data options
    parser.add_argument('--start-lat', type=float, default=37.7749, help='Mock start latitude')
    parser.add_argument('--start-lon', type=float, default=-122.4194, help='Mock start longitude')
    parser.add_argument('--velocity', type=float, default=5.0, help='Mock velocity (m/s)')
    parser.add_argument('--spoof-rate', type=float, default=0.1, help='Mock spoofing rate')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Create GPS data source
        gps_source = create_gps_source(args)
        
        # Initialize components
        logger.info("Initializing real-time GPS spoofing detection...")
        detector = VelocityAnomalyDetector(threshold_mps=args.threshold)
        corrector = PathCorrector()
        reader = GpsReader(gps_source)
        
        # Setup visualization
        plotter = None
        if not args.no_plot:
            try:
                plotter = LivePathPlotter(max_points=args.max_points)
                plotter.setup_plot()
                logger.info("Live visualization ready")
            except Exception as e:
                logger.warning(f"Could not setup visualization: {e}")
        
        # Main processing loop
        logger.info("Starting real-time GPS processing...")
        previous_point = None
        spoofed_count = 0
        total_points = 0
        
        try:
            for current_point in reader.stream():
                total_points += 1
                
                # Detect spoofing
                detector.previous_point = previous_point
                is_spoofed = detector.detect(previous_point, current_point)
                
                # Correct if spoofed
                corrected_point = None
                if is_spoofed:
                    corrected_point = corrector.correct(previous_point, current_point, is_spoofed=True)
                    spoofed_count += 1
                    logger.warning(
                        f" Spoofing detected at point {total_points}: "
                        f"({current_point['latitude']:.6f}, {current_point['longitude']:.6f})"
                    )
                else:
                    corrected_point = current_point
                
                # Update visualization
                if plotter:
                    plotter.add_point(current_point, corrected_point, is_spoofed)
                    if total_points == 1:
                        plotter.start_animation(interval=1000)
                
                # Log progress
                if total_points % 10 == 0:
                    rate = (spoofed_count / total_points) * 100
                    logger.info(
                        f"Processed {total_points} points, "
                        f"detected {spoofed_count} spoofed points ({rate:.1f}% rate)"
                    )
                
                previous_point = current_point
                
        except KeyboardInterrupt:
            logger.info("Processing stopped by user")
        except Exception as e:
            logger.error(f"Error during processing: {e}", exc_info=True)
        finally:
            if plotter:
                plotter.close()
            
            # Final summary
            if total_points > 0:
                rate = (spoofed_count / total_points) * 100
                logger.info(
                    f"\n Processing complete:\n"
                    f"  Total points processed: {total_points}\n"
                    f"  Spoofed points detected: {spoofed_count}\n"
                    f"  Detection rate: {rate:.1f}%\n"
                    f"  Velocity threshold: {args.threshold} m/s"
                )
    
    except Exception as e:
        logger.error(f" Failed to start real-time detection: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()