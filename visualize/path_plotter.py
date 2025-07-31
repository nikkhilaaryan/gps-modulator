import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from matplotlib.patches import Polygon

def plot_spoofing_scenario(
    original_path: List[Dict[str, Any]], 
    spoofed_gps_path: List[Dict[str, Any]], 
    corrected_path: List[Dict[str, Any]],
    spoof_start_idx: int,
    spoof_end_idx: int,
    title: Optional[str] = None,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Visualizes a GPS spoofing attack and correction scenario for a defense-grade autonomous navigation system.

    Parameters:
    - original_path: The true/expected path the vehicle should follow.
    - spoofed_gps_path: The false path reported by compromised GPS.
    - corrected_path: The path after IMU/sensor fusion correction.
    - spoof_start_idx: Index where spoofing attack begins.
    - spoof_end_idx: Index where spoofing attack ends.
    - title: Optional plot title.
    - save_path: Optional file path to save the plot.

    Returns:
    - matplotlib Figure object.
    """
    
    def extract_coords(point: Dict[str, Any]) -> Tuple[float, float]:
        """Extract latitude and longitude from a point dictionary."""
        if 'lat' in point and 'lon' in point:
            return point['lat'], point['lon']
        elif 'latitude' in point and 'longitude' in point:
            return point['latitude'], point['longitude']
        raise ValueError(f"Invalid coordinate format: {point}")

    # Extract coordinates
    orig_lats, orig_lons = zip(*[extract_coords(p) for p in original_path])
    spoof_lats, spoof_lons = zip(*[extract_coords(p) for p in spoofed_gps_path])
    corr_lats, corr_lons = zip(*[extract_coords(p) for p in corrected_path])

    # Create figure with professional styling
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f5f5f5')

    # Plot Original Path (True Path)
    ax.plot(orig_lons, orig_lats, color='#1a3c34', linewidth=3, 
            linestyle='-', label='True Path', zorder=5,
            marker='o', markersize=6, markerfacecolor='#1a3c34', 
            markeredgecolor='white', markeredgewidth=1)

    # Plot Spoofed GPS Path
    # Pre-attack: trusted GPS (simplified to match True Path initially)
    if spoof_start_idx > 0:
        pre_lons = spoof_lons[:spoof_start_idx]
        pre_lats = spoof_lats[:spoof_start_idx]
        ax.plot(pre_lons, pre_lats, color='#4682b4', linewidth=1,
                linestyle='-', alpha=0.5, zorder=3, label='Trusted GPS')

    # During attack: spoofed path
    attack_lons = spoof_lons[spoof_start_idx:spoof_end_idx+1]
    attack_lats = spoof_lats[spoof_start_idx:spoof_end_idx+1]
    if attack_lons:
        ax.plot(attack_lons, attack_lats, color='#b22222', linewidth=2,
                linestyle=':', label='Spoofed GPS', zorder=4,
                marker='x', markersize=8, markerfacecolor='#b22222',
                markeredgecolor='#b22222')

    # Post-attack: trusted GPS restored
    if spoof_end_idx < len(spoof_lons) - 1:
        post_lons = spoof_lons[spoof_end_idx+1:]
        post_lats = spoof_lats[spoof_end_idx+1:]
        ax.plot(post_lons, post_lats, color='#4682b4', linewidth=1,
                linestyle='-', alpha=0.5, zorder=3)

    # Plot Corrected Path
    ax.plot(corr_lons, corr_lats, color='#228b22', linewidth=2.5,
            linestyle='-', label='IMU-Corrected Path', zorder=6,
            marker='^', markersize=6, markerfacecolor='#228b22',
            markeredgecolor='white', markeredgewidth=1)

    # Highlight Attack Zone
    if attack_lons:
        attack_polygon_x = list(attack_lons) + list(corr_lons[spoof_start_idx:spoof_end_idx+1])[::-1]
        attack_polygon_y = list(attack_lats) + list(corr_lats[spoof_start_idx:spoof_end_idx+1])[::-1]
        if len(attack_polygon_x) >= 3:
            attack_zone = Polygon(list(zip(attack_polygon_x, attack_polygon_y)), 
                                 alpha=0.1, facecolor='#b22222', edgecolor='#b22222', 
                                 linewidth=1, linestyle='--', zorder=1,
                                 label='Spoofing Zone')
            ax.add_patch(attack_zone)

    # Add Start and End Markers
    ax.scatter([orig_lons[0]], [orig_lats[0]], color='#1a3c34', s=150, 
               marker='*', edgecolors='white', linewidth=2, zorder=10)
    ax.annotate('Start', (orig_lons[0], orig_lats[0]), 
                xytext=(0, -20), textcoords='offset points', 
                fontsize=10, color='#1a3c34', fontweight='bold',
                ha='center', zorder=11)

    ax.scatter([orig_lons[-1]], [orig_lats[-1]], color='#1a3c34', s=150, 
               marker='*', edgecolors='white', linewidth=2, zorder=10)
    ax.annotate('End', (orig_lons[-1], orig_lats[-1]), 
                xytext=(0, 20), textcoords='offset points', 
                fontsize=10, color='#1a3c34', fontweight='bold',
                ha='center', zorder=11)

    # Add minimal annotations for attack points
    for i in range(spoof_start_idx, min(spoof_end_idx + 1, len(spoof_lats))):
        spoof_lat, spoof_lon = spoof_lats[i], spoof_lons[i]
        ax.annotate(f'S{i}', (spoof_lon, spoof_lat), 
                    xytext=(10, -10), textcoords='offset points', 
                    fontsize=8, color='#b22222', fontweight='bold',
                    ha='center', zorder=12)

    # Styling
    ax.set_xlabel("Longitude (°)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Latitude (°)", fontsize=12, fontweight='bold')
    ax.set_title(title or "GPS Spoofing Attack and IMU Correction", 
                 fontsize=14, fontweight='bold', pad=15)

    # Legend
    legend = ax.legend(loc='upper left', fontsize=10, framealpha=0.95,
                      bbox_to_anchor=(0.02, 0.98))
    legend.get_frame().set_edgecolor('#333333')
    legend.get_frame().set_linewidth(1)

    # Grid and axis limits
    ax.grid(True, alpha=0.3, linestyle='--')
    all_lons = list(orig_lons) + list(spoof_lons) + list(corr_lons)
    all_lats = list(orig_lats) + list(spoof_lats) + list(corr_lats)
    lon_margin = (max(all_lons) - min(all_lons)) * 0.15
    lat_margin = (max(all_lats) - min(all_lats)) * 0.15
    ax.set_xlim(min(all_lons) - lon_margin, max(all_lons) + lon_margin)
    ax.set_ylim(min(all_lats) - lat_margin, max(all_lats) + lat_margin)

    # Status panel moved to lower-right to avoid overlapping end point
    attack_duration = spoof_end_idx - spoof_start_idx + 1
    total_points = len(original_path)
    attack_percentage = (attack_duration / total_points) * 100
    max_deviation = max(
        ((spoof_lats[i] - orig_lats[i])**2 + (spoof_lons[i] - orig_lons[i])**2)**0.5 * 111000
        for i in range(spoof_start_idx, min(spoof_end_idx + 1, len(spoof_lats)))
    ) if attack_lons else 0

    status_text = (
        f"Attack Duration: {attack_duration}/{total_points} points ({attack_percentage:.1f}%)\n"
        f"Max Deviation: {max_deviation:.0f} m\n"
        f"Correction: Successful"
    )
    ax.text(0.98, 0.02, status_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right', 
            bbox=dict(boxstyle='square,pad=0.5', facecolor='white', 
                      edgecolor='#333333', alpha=0.95), 
            fontfamily='monospace')

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig

def create_demo_scenario() -> Tuple[List[Dict[str, float]], List[Dict[str, float]], List[Dict[str, float]], int, int]:
    """Create a realistic GPS spoofing scenario with believable deviations."""
    original_route = [
        {'lat': 19.0760, 'lon': 72.8777},  # Start
        {'lat': 19.0765, 'lon': 72.8782},
        {'lat': 19.0770, 'lon': 72.8787},
        {'lat': 19.0775, 'lon': 72.8792},  # Attack starts
        {'lat': 19.0780, 'lon': 72.8797},
        {'lat': 19.0785, 'lon': 72.8802},  # Attack ends
        {'lat': 19.0790, 'lon': 72.8807},
        {'lat': 19.0795, 'lon': 72.8812},  # End
    ]

    # Spoofed path with realistic deviations (50-100m)
    spoofed_gps = [
        {'lat': 19.0760, 'lon': 72.8777},
        {'lat': 19.0765, 'lon': 72.8782},
        {'lat': 19.0770, 'lon': 72.8787},
        {'lat': 19.0777, 'lon': 72.8800},  # ~80m deviation
        {'lat': 19.0783, 'lon': 72.8805},  # ~60m deviation
        {'lat': 19.0787, 'lon': 72.8810},  # ~50m deviation
        {'lat': 19.0790, 'lon': 72.8807},
        {'lat': 19.0795, 'lon': 72.8812},
    ]

    # Corrected path stays close to original
    corrected_path = [
        {'lat': 19.0760, 'lon': 72.8777},
        {'lat': 19.0765, 'lon': 72.8782},
        {'lat': 19.0770, 'lon': 72.8787},
        {'lat': 19.0776, 'lon': 72.8793},  # ~10m deviation
        {'lat': 19.0781, 'lon': 72.8798},  # ~10m deviation
        {'lat': 19.0786, 'lon': 72.8803},  # ~10m deviation
        {'lat': 19.0790, 'lon': 72.8807},
        {'lat': 19.0795, 'lon': 72.8812},
    ]

    return original_route, spoofed_gps, corrected_path, 3, 5

if __name__ == "__main__":
    print("=== GPS Spoofing Visualization Demo ===")
    original, spoofed, corrected, attack_start, attack_end = create_demo_scenario()
    fig = plot_spoofing_scenario(
        original_path=original,
        spoofed_gps_path=spoofed,
        corrected_path=corrected,
        spoof_start_idx=attack_start,
        spoof_end_idx=attack_end,
        title="GPS Spoofing Attack and IMU Correction",
        save_path="gps_spoofing_defense.png"
    )
    plt.show()
    print("Demo completed.")