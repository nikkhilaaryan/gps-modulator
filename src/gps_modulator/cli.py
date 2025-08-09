"""Command-line interface for GPS spoofing detection system."""

import argparse
import logging
import sys
import csv
from typing import Dict, Any

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from .detectors import VelocityAnomalyDetector
from .correction import PathCorrector
from .streaming import GpsReader, MockGpsGenerator
from .visualization import LivePathPlotter


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


def csv_stream_source(filepath):
    """Yield GPS points from a CSV file with columns: latitude, longitude, altitude, timestamp."""
    import csv
    with open(filepath, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                yield {
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'altitude': float(row['altitude']),
                    'timestamp': float(row['timestamp'])
                }
            except Exception as e:
                print(f"Skipping row due to error: {e} -- {row}")
def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description='Real-time GPS spoofing detection and correction system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --threshold 30 --no-plot
  %(prog)s --threshold 25 --max-points 500 --update-interval 50
  %(prog)s --verbose --threshold 20
        """
    )
    
    parser.add_argument(
        '--threshold',
        type=float,
        default=50.0,
        help='Velocity threshold for spoofing detection (m/s, default: 50.0)'
    )
    
    parser.add_argument(
        '--max-points',
        type=int,
        default=1000,
        help='Maximum number of points to display on plot (default: 1000)'
    )
    
    parser.add_argument(
        '--update-interval',
        type=int,
        default=100,
        help='Plot update interval in milliseconds (default: 100)'
    )
    
    parser.add_argument(
        '--no-plot',
        action='store_true',
        help='Disable live plotting (useful for headless environments)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--csv',
        type=str,
        default=None,
        help='Path to CSV file with GPS data (columns: lat, lon, timestamp)'
    )
    
    return parser


def run_detection_system(args: argparse.Namespace) -> None:
    """
    Run the main GPS spoofing detection system.
    
    Args:
        args: Parsed command-line arguments
    """
    logger = logging.getLogger(__name__)
    
    # Initialize components
    logger.info("Initializing GPS spoofing detection system...")
    
    detector = VelocityAnomalyDetector(threshold_velocity=args.threshold)
    corrector = PathCorrector()
    
    # Choose GPS data source
    if args.csv:
        logger.info(f"Using CSV file as GPS data source: {args.csv}")
        gps_reader = GpsReader(lambda: csv_stream_source(args.csv))
    else:
        # Create mock GPS generator
        gps_generator = MockGpsGenerator(
            start_lat=37.7749,
            start_lon=-122.4194,
            velocity_mps=5.0,
            spoof_rate=0.15,
            spoof_magnitude=0.001
        )
        gps_reader = GpsReader(gps_generator.generate)
    
    # Initialize plotter if not disabled
    plotter = None
    if not args.no_plot:
        logger.info("Setting up live visualization...")
        plotter = LivePathPlotter(max_points=args.max_points)
        plotter.setup_plot()
    
    logger.info("Starting GPS data processing...")
    
    previous_point: Dict[str, Any] = None
    spoofed_count = 0
    total_points = 0
    
    try:
        for current_point in gps_reader.stream():
            total_points += 1
            
            # Detect spoofing
            detector.previous_point = previous_point
            is_spoofed = detector.detect(current_point)
            
            # Correct if spoofed
            corrected_point = None
            if is_spoofed:
                corrected_point = corrector.correct(
                    current_point, is_spoofed=is_spoofed
                )
                spoofed_count += 1
                logger.warning(
                    f"Spoofing detected at point {total_points}: "
                    f"({current_point['latitude']:.6f}, {current_point['longitude']:.6f})"
                )
            
            # Update visualization
            if plotter:
                plotter.add_point(
                    raw_point=current_point,
                    corrected_point=corrected_point or current_point,
                    is_spoofed=is_spoofed
                )
                
                # Start animation on first point
                if total_points == 1:
                    plotter.start_animation(interval=args.update_interval)
            
            # Log progress
            if total_points % 50 == 0:
                logger.info(
                    f"Processed {total_points} points, "
                    f"detected {spoofed_count} spoofed points "
                    f"({(spoofed_count/total_points)*100:.1f}% rate)"
                )
            
            previous_point = current_point
            
            # Allow graceful shutdown
            # if not args.no_plot and not plt.fignum_exists(plotter.fig.number if plotter else 0):
            #     logger.info("Visualization window closed by user")
            #     break
                
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
    finally:
        if plotter:
            plotter.close()
            if plt and not args.no_plot:
                plt.show()
                input("Press Enter to exit...")
        
        # Print summary
        if total_points > 0:
            logger.info(
                f"\nProcessing complete:\n"
                f"  Total points processed: {total_points}\n"
                f"  Spoofed points detected: {spoofed_count}\n"
                f"  Detection rate: {(spoofed_count/total_points)*100:.1f}%\n"
                f"  Velocity threshold: {args.threshold} m/s"
            )


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    try:
        run_detection_system(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


# Import plt for graceful shutdown handling
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None