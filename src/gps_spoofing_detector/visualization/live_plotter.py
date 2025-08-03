"""Real-time GPS path visualization with spoofing detection."""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import PathCollection
from typing import List, Dict, Any, Optional, Tuple
import threading
import time


class LivePathPlotter:
    """
    Real-time GPS path visualization with spoofing detection overlay.
    
    This class provides live plotting capabilities for GPS paths, showing both
    raw and corrected paths with visual indicators for detected spoofing.
    """
    
    def __init__(self, max_points: int = 1000, title: str = "GPS Spoofing Detection"):
        """
        Initialize the live path plotter.
        
        Args:
            max_points: Maximum number of points to display on plot
            title: Plot title
        """
        self.max_points = max_points
        self.title = title
        
        # Data storage
        self.raw_lats: List[float] = []
        self.raw_lons: List[float] = []
        self.corrected_lats: List[float] = []
        self.corrected_lons: List[float] = []
        self.spoofed_indices: List[int] = []
        
        # Plotting state
        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[plt.Axes] = None
        self.raw_line: Optional[plt.Line2D] = None
        self.corrected_line: Optional[plt.Line2D] = None
        self.spoofed_scatter: Optional[PathCollection] = None
        
        # Threading
        self._lock = threading.Lock()
        self._animation: Optional[animation.FuncAnimation] = None
        self._is_running = False
    
    def setup_plot(self) -> None:
        """Initialize the matplotlib plot."""
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        
        # Initialize empty lines
        self.raw_line, = self.ax.plot([], [], 'b-', alpha=0.6, 
                                      label='Raw GPS Path', linewidth=2)
        self.corrected_line, = self.ax.plot([], [], 'g-', 
                                          label='Corrected Path', linewidth=2)
        
        # Initialize empty scatter for spoofed points
        self.spoofed_scatter = self.ax.scatter([], [], c='red', 
                                             s=50, alpha=0.7, 
                                             label='Detected Spoofing')
        
        # Configure plot
        self.ax.set_xlabel('Longitude')
        self.ax.set_ylabel('Latitude')
        self.ax.set_title(self.title)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        
        # Enable interactive mode
        plt.ion()
    
    def add_point(self, 
                  raw_point: Dict[str, float],
                  corrected_point: Optional[Dict[str, float]] = None,
                  is_spoofed: bool = False) -> None:
        """
        Add a new GPS point to the visualization.
        
        Args:
            raw_point: Original GPS point with 'latitude' and 'longitude'
            corrected_point: Corrected GPS point (if available)
            is_spoofed: Whether this point was detected as spoofed
        """
        with self._lock:
            # Add raw coordinates
            self.raw_lats.append(raw_point['latitude'])
            self.raw_lons.append(raw_point['longitude'])
            
            # Add corrected coordinates
            if corrected_point:
                self.corrected_lats.append(corrected_point['latitude'])
                self.corrected_lons.append(corrected_point['longitude'])
            else:
                # Use raw point if no correction
                self.corrected_lats.append(raw_point['latitude'])
                self.corrected_lons.append(raw_point['longitude'])
            
            # Track spoofed indices
            if is_spoofed:
                self.spoofed_indices.append(len(self.raw_lats) - 1)
            
            # Limit data to max_points
            self._limit_data()
    
    def _limit_data(self) -> None:
        """Limit stored data to max_points."""
        if len(self.raw_lats) > self.max_points:
            self.raw_lats = self.raw_lats[-self.max_points:]
            self.raw_lons = self.raw_lons[-self.max_points:]
            self.corrected_lats = self.corrected_lats[-self.max_points:]
            self.corrected_lons = self.corrected_lons[-self.max_points:]
            
            # Adjust spoofed indices
            offset = len(self.raw_lats) - len(self.spoofed_indices)
            self.spoofed_indices = [i - offset for i in self.spoofed_indices 
                                  if i >= offset]
    
    def update_plot(self, frame: Any) -> Tuple[plt.Line2D, plt.Line2D, PathCollection]:
        """
        Update the plot with current data.
        
        Args:
            frame: Animation frame (required by FuncAnimation)
        
        Returns:
            Tuple of updated plot elements
        """
        with self._lock:
            if not self.raw_lats:
                return self.raw_line, self.corrected_line, self.spoofed_scatter
            
            # Update raw path
            self.raw_line.set_data(self.raw_lons, self.raw_lats)
            
            # Update corrected path
            self.corrected_line.set_data(self.corrected_lons, self.corrected_lats)
            
            # Update spoofed points
            if self.spoofed_indices:
                spoofed_lats = [self.raw_lats[i] for i in self.spoofed_indices 
                               if i < len(self.raw_lats)]
                spoofed_lons = [self.raw_lons[i] for i in self.spoofed_indices 
                               if i < len(self.raw_lons)]
                
                if spoofed_lats and spoofed_lons:
                    self.spoofed_scatter.set_offsets(
                        list(zip(spoofed_lons, spoofed_lats))
                    )
            else:
                self.spoofed_scatter.set_offsets([])
            
            # Auto-scale axes
            if self.raw_lats:
                lat_min, lat_max = min(self.raw_lats), max(self.raw_lats)
                lon_min, lon_max = min(self.raw_lons), max(self.raw_lons)
                
                # Add padding
                lat_padding = (lat_max - lat_min) * 0.1 or 0.001
                lon_padding = (lon_max - lon_min) * 0.1 or 0.001
                
                self.ax.set_xlim(lon_min - lon_padding, lon_max + lon_padding)
                self.ax.set_ylim(lat_min - lat_padding, lat_max + lat_padding)
        
        return self.raw_line, self.corrected_line, self.spoofed_scatter
    
    def start_animation(self, interval: int = 100) -> None:
        """
        Start the live animation.
        
        Args:
            interval: Update interval in milliseconds
        """
        if not self.fig:
            self.setup_plot()
        
        self._animation = animation.FuncAnimation(
            self.fig, 
            self.update_plot,
            interval=interval,
            blit=True,
            cache_frame_data=False
        )
        
        self._is_running = True
        plt.show()
    
    def stop_animation(self) -> None:
        """Stop the live animation."""
        if self._animation:
            self._animation.event_source.stop()
            self._is_running = False
    
    def clear(self) -> None:
        """Clear all stored data."""
        with self._lock:
            self.raw_lats.clear()
            self.raw_lons.clear()
            self.corrected_lats.clear()
            self.corrected_lons.clear()
            self.spoofed_indices.clear()
    
    def close(self) -> None:
        """Close the plot window."""
        if self.fig:
            plt.close(self.fig)
            self.fig = None
            self.ax = None
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get current visualization statistics.
        
        Returns:
            Dict[str, int]: Statistics including total points and spoofed count
        """
        with self._lock:
            return {
                'total_points': len(self.raw_lats),
                'spoofed_points': len(self.spoofed_indices)
            }