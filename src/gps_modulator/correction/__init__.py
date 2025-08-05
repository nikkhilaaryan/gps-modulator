"""GPS path correction strategies.

This module provides various strategies for correcting GPS paths when
spoofing is detected, including dead reckoning and fallback methods.
"""

from .path_corrector import PathCorrector
from .dead_reckoner import DeadReckoner

__all__ = ["PathCorrector", "DeadReckoner"]