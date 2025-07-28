# GPS Modulator
A modular GPS spoofing detection and path correction system for real-time navigation resilience.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> **Note:** This project is currently under active development. Interfaces and internal modules are subject to change until a stable release.


## Features

- Real-time GPS spoofing detection based on velocity anomaly analysis
- Seamless fallback to dead reckoning using IMU data during spoofing
- Automatic recovery and reintegration of GPS data post-spoofing
- Path visualization for GPS, spoofed, and corrected trajectories
- Modular architecture supporting custom detection and defense modules

## Installation

It is recommended to use a Python virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate    # On Unix or MacOS
.venv\Scripts\activate       # On Windows

pip install -r requirements.txt
```


## Usage

The package can be used to detect GPS spoofing and maintain path continuity in real time.

To simulate a spoofing scenario with visualization:

```bash
python -m tests.test_pipeline_visual
This will run the full detection pipeline and render the true, spoofed, and corrected trajectories.
```

To test individual modules, such as dead reckoning or fallback management:

```bash
pytest -s tests/test_dead_reckoner.py
pytest -s tests/test_fallback_manager.py
```
For integration into an external system, import and initialize the detection pipeline:

```bash
from gps_modulator.core.detection_pipeline import DetectionPipeline
```
## Roadmap

The following features are planned for future releases:

- Real-time integration with external GPS and IMU hardware sources
- Automatic calibration of velocity thresholds based on object type
- Additional spoofing detection techniques (e.g., location drift, bearing anomalies)
- Support for 3D path visualization and elevation data
- REST API interface for live system integration
- Extended logging and telemetry export to CSV/JSON
- CLI tool for batch analysis of GPS datasets

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


## Author

**Aryan Raj** 
For questions, collaborations, or feedback: [nikhilaryan0928@gmail.com](mailto:nikhilaryan0928@gmail.com)
