# gps-modulator

A comprehensive Python package for real-time detection and correction of GPS spoofing attacks using velocity-based anomaly detection and dead reckoning techniques.

## Features

- **Real-time GPS spoofing detection** using velocity anomaly analysis
- **Automatic correction** of spoofed GPS points using dead reckoning
- **Live visualization** of GPS paths with spoofing indicators
- **Modular architecture** for easy extension and testing
- **Command-line interface** with configurable parameters
- **Mock data generation** for testing and demonstration

## Architecture

The system is organized into modular components:

```
gps-spoofing-detector/
├── src/
│   └── gps_spoofing_detector/
│       ├── __init__.py
│       ├── cli.py                 # Command-line interface
│       ├── detectors/             # Spoofing detection algorithms
│       │   ├── __init__.py
│       │   └── velocity_anomaly_detector.py
│       ├── correction/            # GPS correction methods
│       │   ├── __init__.py
│       │   ├── path_corrector.py
│       │   └── dead_reckoner.py
│       ├── streaming/             # GPS data streaming
│       │   ├── __init__.py
│       │   ├── gps_reader.py
│       │   └── data_generators.py
│       ├── visualization/           # Real-time plotting
│       │   ├── __init__.py
│       │   └── live_plotter.py
│       └── utils/                   # Mathematical utilities
│           ├── __init__.py
│           └── gps_math.py
├── tests/                         # Unit tests
├── examples/                      # Usage examples
├── docs/                          # Documentation
├── setup.py                       # Package configuration
└── README.md
```

## Installation

### From Source

```bash
git clone <repository-url>
cd gps-spoofing-detector
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

```bash
# Basic usage with live plotting
gps-spoofing-detector

# Disable plotting (headless mode)
gps-spoofing-detector --no-plot

# Custom velocity threshold
gps-spoofing-detector --threshold 30.0

# Verbose logging with custom parameters
gps-spoofing-detector --threshold 25 --max-points 500 --verbose
```

### Python API Usage

```python
from gps_spoofing_detector import (
    VelocityAnomalyDetector,
    PathCorrector,
    GpsReader,
    LivePathPlotter,
    MockGpsGenerator
)

# Initialize components
detector = VelocityAnomalyDetector(threshold_mps=50.0)
corrector = PathCorrector()

# Create mock data source
generator = MockGpsGenerator()
gps_reader = GpsReader(generator.generate)

# Process GPS data
previous_point = None
for point in gps_reader.stream():
    is_spoofed = detector.detect(previous_point, point)
    if is_spoofed:
        corrected_point = corrector.correct(previous_point, point, is_spoofed=True)
        print(f"Spoofing detected and corrected: {corrected_point}")
    previous_point = point
```

## Configuration

### Command Line Options

- `--threshold`: Velocity threshold for spoofing detection (m/s, default: 50.0)
- `--max-points`: Maximum points to display on plot (default: 1000)
- `--update-interval`: Plot update interval in milliseconds (default: 100)
- `--no-plot`: Disable live plotting
- `--verbose`: Enable verbose logging

### Detector Configuration

```python
from gps_spoofing_detector.detectors import VelocityAnomalyDetector

# Create detector with custom threshold
detector = VelocityAnomalyDetector(threshold_mps=30.0)
```

### Mock Data Configuration

```python
from gps_spoofing_detector.streaming import MockGpsGenerator

# Configure mock data with custom parameters
generator = MockGpsGenerator(
    start_lat=37.7749,        # Starting latitude
    start_lon=-122.4194,      # Starting longitude
    velocity_mps=5.0,         # Base velocity (m/s)
    spoof_rate=0.15,          # Probability of spoofing (0-1)
    spoof_magnitude=0.001      # Spoofing magnitude (degrees)
)
```

## API Reference

### Core Classes

#### `VelocityAnomalyDetector`

Detects GPS spoofing based on unrealistic velocity changes.

```python
detector = VelocityAnomalyDetector(threshold_mps=50.0)
is_spoofed = detector.detect(previous_point, current_point)
```

#### `PathCorrector`

Corrects spoofed GPS points using dead reckoning.

```python
corrector = PathCorrector()
corrected_point = corrector.correct(previous_point, spoofed_point, is_spoofed=True)
```

#### `GpsReader`

Reads and validates GPS data from streaming sources.

```python
reader = GpsReader(data_source)
for point in reader.stream():
    process_point(point)
```

#### `LivePathPlotter`

Real-time visualization of GPS paths with spoofing indicators.

```python
plotter = LivePathPlotter(max_points=1000)
plotter.add_point(raw_point, corrected_point, is_spoofed=True)
plotter.start_animation()
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest tests/ --cov=gps_spoofing_detector
```

## Development

### Code Style

This project follows PEP 8 conventions:
- Snake_case for functions and variables
- PascalCase for classes
- Type hints for all public APIs
- Comprehensive docstrings

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes with tests
4. Ensure code passes linting (`flake8 src/`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run code formatting
black src/ tests/

# Run type checking
mypy src/

# Run linting
flake8 src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python and matplotlib for visualization
- Uses haversine formula for accurate distance calculations
- Designed for real-world GPS spoofing detection applications

## Author

**ARYAN RAJ**  
Email: nikhilaryan0928@gmail.com

