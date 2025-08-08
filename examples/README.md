# GPS Spoofing Detector Examples

This directory contains comprehensive examples demonstrating how to use the GPS spoofing detection system. Each example serves a specific purpose and showcases different aspects of the library.

## Quick Start Examples

### 1. Static Demo (`static_demo.py`)
**Most reliable - guaranteed to work**

A simple static plot that demonstrates GPS spoofing detection without any animation issues.

```bash
python static_demo.py
```

**Features:**
- No animation or streaming complexity
- Guaranteed to display on all platforms
- Shows clear spoofing vs normal GPS data
- Perfect for first-time users

### 2. Simple Demo (`simple_demo.py`)
**Interactive demonstration**

Shows real-time GPS spoofing detection with live updates.

```bash
python simple_demo.py
```

**Features:**
- Live GPS path generation
- Real-time spoofing detection
- Clear visual indicators
- Windows-compatible

### 3. Windows Demo (`windows_demo.py`)
**Windows-optimized**

Specifically designed for Windows environments with enhanced display handling.

```bash
python windows_demo.py
```

**Features:**
- Forces TkAgg backend
- Window management for visibility
- Square path pattern for clarity
- Enhanced error handling

## Advanced Examples

### 4. IMU Integration Demo (`imu_integration_demo.py`)
**Complete GPS + IMU system**

Demonstrates how IMU data can be used to correct GPS spoofing attacks.

```bash
python imu_integration_demo.py
```

**Features:**
- Story-driven visualization
- IMU-assisted path correction
- Magnetic declination handling
- Comprehensive spoofing mitigation

### 5. Test Visualization (`test_visualization.py`)
**Development testing**

Simple test to verify the visualization system is working correctly.

```bash
python test_visualization.py
```

**Features:**
- Minimal complexity
- Quick verification
- Sample data generation
- Basic functionality test

### 6. Diagnostic Tool (`diagnostic.py`)
**Troubleshooting**

Helps diagnose and fix matplotlib display issues.

```bash
python diagnostic.py
```

**Features:**
- System information display
- Backend compatibility check
- Display environment analysis
- Automated troubleshooting

## Usage Guide

### For Beginners
Start with the static demo to understand the basic concepts:

```bash
# Step 1: Install the package
pip install -e ..

# Step 2: Run the static demo
python static_demo.py

# Step 3: Try the interactive demo
python simple_demo.py
```

### For Windows Users
Use the Windows-optimized examples:

```bash
# Windows-specific demo
python windows_demo.py

# If issues persist, run diagnostics
python diagnostic.py
```

### For Advanced Users
Explore IMU integration and custom configurations:

```bash
# Full IMU integration demo
python imu_integration_demo.py

# Custom threshold testing
python ../src/gps_modulator/cli.py --threshold 25 --verbose
```

## Common Issues and Solutions

### "No module named 'gps_modulator'"
```bash
# Install the package in development mode
cd .. && pip install -e .
```

### Window Doesn't Appear (Windows)
```bash
# Use Windows-specific demo
python windows_demo.py

# Or run diagnostic
python diagnostic.py
```

### Window Closes Immediately
```bash
# Use static demo (guaranteed to stay open)
python static_demo.py
```

### Slow Performance
```bash
# Use static demo for faster rendering
python static_demo.py

# Or reduce points in interactive demos
python simple_demo.py  # Has fewer points by default
```

## Customization Examples

### Custom GPS Path
```python
from gps_modulator import EnhancedGpsReader

# Create custom GPS path
reader = EnhancedGpsReader(
    start_lat=37.7749,    # San Francisco
    start_lon=-122.4194,
    velocity_mps=15.0,    # 15 m/s (~33 mph)
    spoof_rate=0.2        # 20% spoofing probability
)
```

### Custom Detection Threshold
```python
from gps_modulator import VelocityAnomalyDetector

# Lower threshold for more sensitive detection
detector = VelocityAnomalyDetector(threshold_mps=25.0)
```

### Custom Visualization
```python
from gps_modulator import LivePathPlotter

# Configure plot appearance
plotter = LivePathPlotter(
    max_points=500,
    title="My GPS Spoofing Detection",
    figsize=(12, 8)
)
```

## Platform-Specific Notes

### Windows
- All examples include Windows-specific fixes
- Use `windows_demo.py` for best compatibility
- Run `diagnostic.py` if issues occur

### Linux/macOS
- Examples should work out of the box
- Use `static_demo.py` for quick testing
- Consider `simple_demo.py` for interactive demos

### WSL (Windows Subsystem for Linux)
- May require X11 server setup
- Use `static_demo.py` as fallback
- Run `diagnostic.py` for troubleshooting

## Next Steps

After running the examples:

1. **Read the main README** for detailed API documentation
2. **Check the CLI documentation** for command-line usage
3. **Explore the source code** in `../src/gps_modulator/`
4. **Run the test suite** with `pytest ../tests/`
5. **Integrate into your own projects** using the API examples

## Support

If you encounter issues:
1. Run `python diagnostic.py` for troubleshooting
2. Check the main README troubleshooting section
3. Open an issue on GitHub with your diagnostic output