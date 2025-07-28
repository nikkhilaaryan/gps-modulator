import matplotlib.pyplot as plt
import numpy as np

def plot_paths(gps_path, fallback_path=None, spoof_flags=None):
    """
    Visualizes GNSS signal integrity analysis and autonomous navigation path correction.
    Displays trusted positioning data, compromised signals, and corrected trajectory.
    
    Parameters:
    gps_path: List of {'lat': float, 'lon': float} - Raw GNSS position data
    fallback_path: List of {'lat': float, 'lon': float} or None - IMU-derived position estimates
    spoof_flags: List of bool - Signal integrity flags indicating compromised data points
    """
    if not gps_path or len(gps_path) == 0:
        print("Error: No GNSS data provided for analysis")
        return
    
    gps_lats = [p['lat'] for p in gps_path]
    gps_lons = [p['lon'] for p in gps_path]

    # Create professional figure with appropriate dimensions
    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f8f9fa')
    
    # Initialize path segments for analysis
    trusted_segments = []
    compromised_segments = []
    corrected_trajectory = []
    
    if spoof_flags and fallback_path:
        # Analyze signal integrity and generate corrected trajectory
        for i in range(len(gps_path)):
            current_point = gps_path[i]
            signal_compromised = spoof_flags[i] if i < len(spoof_flags) else False
            fallback_estimate = fallback_path[i] if i < len(fallback_path) else None
            
            if signal_compromised:
                compromised_segments.append((i, current_point))
                # Use fallback estimate for corrected trajectory
                if fallback_estimate is not None:
                    corrected_trajectory.append((i, fallback_estimate))
                else:
                    corrected_trajectory.append((i, current_point))
            else:
                trusted_segments.append((i, current_point))
                # Use trusted GNSS data for corrected trajectory
                corrected_trajectory.append((i, current_point))
        
        # Sort corrected trajectory by temporal index
        corrected_trajectory.sort(key=lambda x: x[0])
    else:
        # If no integrity flags provided, treat all data as trusted
        trusted_segments = [(i, point) for i, point in enumerate(gps_path)]
        corrected_trajectory = trusted_segments.copy()
    
    # Plot 1: Raw GNSS trajectory (reference baseline)
    ax.plot(gps_lons, gps_lats, color='#cccccc', linewidth=2, alpha=0.6, 
            linestyle='--', label='Raw GNSS Signal Chain', zorder=1)
    ax.scatter(gps_lons, gps_lats, color='#cccccc', s=30, alpha=0.5, zorder=2)
    
    # Plot 2: Trusted GNSS positions
    if trusted_segments:
        trusted_indices, trusted_points = zip(*trusted_segments)
        trusted_lats = [p['lat'] for p in trusted_points]
        trusted_lons = [p['lon'] for p in trusted_points]
        
        # Connect consecutive trusted points
        prev_idx = None
        for i, (idx, point) in enumerate(trusted_segments):
            if prev_idx is not None and idx == prev_idx + 1:
                prev_point = trusted_segments[i-1][1]
                ax.plot([prev_point['lon'], point['lon']], 
                       [prev_point['lat'], point['lat']], 
                       color='#2e7d32', linewidth=3, alpha=0.9, zorder=4)
            prev_idx = idx
        
        ax.scatter(trusted_lons, trusted_lats, color='#2e7d32', s=100, zorder=6, 
                  marker='o', edgecolors='#1b5e20', linewidth=2, 
                  label='Verified GNSS Positions')
        
        # Annotate trusted positions
        trusted_count = 0
        for i, point in trusted_segments:
            ax.annotate(f'T{trusted_count}', (point['lon'], point['lat']), 
                       xytext=(12, 12), textcoords='offset points', 
                       fontsize=10, color='#1b5e20', fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='#e8f5e8', 
                               edgecolor='#2e7d32', alpha=0.9),
                       zorder=10)
            trusted_count += 1
    
    # Plot 3: Compromised signal positions
    if compromised_segments:
        comp_indices, comp_points = zip(*compromised_segments)
        comp_lats = [p['lat'] for p in comp_points]
        comp_lons = [p['lon'] for p in comp_points]
        
        ax.scatter(comp_lons, comp_lats, color='#d32f2f', s=180, zorder=8,
                  marker='X', linewidth=3, edgecolors='#b71c1c',
                  label='Compromised GNSS Signals')
        
        # Annotate compromised positions
        compromised_count = 0
        for idx, point in compromised_segments:
            ax.annotate(f'C{compromised_count}', (point['lon'], point['lat']), 
                       xytext=(15, -20), textcoords='offset points', 
                       fontsize=10, color='#b71c1c', fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='#ffebee', 
                               edgecolor='#d32f2f', alpha=0.95),
                       zorder=10)
            compromised_count += 1

    
    # Plot 4: IMU-derived fallback estimates
    if fallback_path and spoof_flags:
        fallback_estimates = []
        for i, (fb_point, is_compromised) in enumerate(zip(fallback_path, spoof_flags)):
            if fb_point is not None and is_compromised:
                fallback_estimates.append((i, fb_point))
        
        if fallback_estimates:
            fb_indices, fb_points = zip(*fallback_estimates)
            fb_lats = [p['lat'] for p in fb_points]
            fb_lons = [p['lon'] for p in fb_points]
            
            ax.scatter(fb_lons, fb_lats, color='#f57c00', s=120, zorder=7,
                      marker='s', edgecolors='#e65100', linewidth=2, 
                      label='IMU-Derived Position Estimates')
            
            # Annotate fallback estimates
            fallback_count = 0
            for idx, (i, point) in enumerate(fallback_estimates):
                ax.annotate(f'F{fallback_count}', (point['lon'], point['lat']), 
                           xytext=(-15, 20), textcoords='offset points', 
                           fontsize=10, color='#e65100', fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='#fff3e0', 
                                   edgecolor='#f57c00', alpha=0.95),
                           zorder=10)
    
    # Plot 5: Final corrected trajectory
    if corrected_trajectory and len(corrected_trajectory) > 1:
        corr_indices, corr_points = zip(*corrected_trajectory)
        corr_lats = [p['lat'] for p in corr_points]
        corr_lons = [p['lon'] for p in corr_points]
        
        # Plot corrected trajectory as primary navigation path
        ax.plot(corr_lons, corr_lats, color='#6a1b9a', linewidth=4, 
               alpha=0.8, linestyle='-', label='Corrected Navigation Trajectory', zorder=5)
        
        # Add small markers on the corrected path for clarity
        ax.scatter(corr_lons, corr_lats, color='#6a1b9a', s=40, alpha=0.6, zorder=5)
        
        # Add sequential labels for corrected trajectory waypoints
        for idx, (i, point) in enumerate(corrected_trajectory):
            ax.annotate(f'W{i}', (point['lon'], point['lat']), 
                       xytext=(0, -35), textcoords='offset points', 
                       fontsize=9, color='#4a148c', fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.2", facecolor='#f3e5f5', 
                               edgecolor='#6a1b9a', alpha=0.8),
                       zorder=9, ha='center')
        
        # Add trajectory direction indicators
        for i in range(0, len(corr_lons)-1, max(1, len(corr_lons)//6)):
            if i < len(corr_lons)-1:
                dx = corr_lons[i+1] - corr_lons[i]
                dy = corr_lats[i+1] - corr_lats[i]
                if abs(dx) > 1e-10 or abs(dy) > 1e-10:  # Avoid zero-length arrows
                    ax.annotate('', xy=(corr_lons[i+1], corr_lats[i+1]), 
                               xytext=(corr_lons[i], corr_lats[i]),
                               arrowprops=dict(arrowstyle='->', color='#6a1b9a', 
                                             lw=2, alpha=0.7))
    
    # Professional styling and annotations
    ax.set_xlabel("Longitude (decimal degrees)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Latitude (decimal degrees)", fontsize=12, fontweight='bold')
    ax.set_title("Autonomous Navigation System: GNSS Signal Integrity Analysis\n" + 
                "Signal Verification, Threat Detection, and Trajectory Correction", 
                fontsize=14, fontweight='bold', pad=20)
    
    # Configure legend with professional styling
    legend = ax.legend(loc='upper left', fontsize=10, framealpha=0.95,
                      bbox_to_anchor=(0.02, 0.98), fancybox=True, shadow=True)
    legend.get_frame().set_facecolor('#ffffff')
    legend.get_frame().set_edgecolor('#cccccc')
    
    # Configure grid and axis properties
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.tick_params(axis='both', which='major', labelsize=10)
    
    # Set appropriate axis limits with margin
    if gps_lons and gps_lats:
        all_lons = gps_lons.copy()
        all_lats = gps_lats.copy()
        
        # Include fallback points for proper scaling
        if fallback_path:
            for fb in fallback_path:
                if fb is not None:
                    all_lons.append(fb['lon'])
                    all_lats.append(fb['lat'])
        
        if len(set(all_lons)) > 1 and len(set(all_lats)) > 1:
            lon_margin = (max(all_lons) - min(all_lons)) * 0.15
            lat_margin = (max(all_lats) - min(all_lats)) * 0.15
            ax.set_xlim(min(all_lons) - lon_margin, max(all_lons) + lon_margin)
            ax.set_ylim(min(all_lats) - lat_margin, max(all_lats) + lat_margin)
    
    # Add system status information panel
    analysis_text = """NAVIGATION SYSTEM STATUS:
• Signal Integrity: MONITORING
• Threat Detection: ACTIVE  
• Fallback Systems: OPERATIONAL
• Trajectory Correction: ENABLED"""
    
    props = dict(boxstyle='round,pad=0.5', facecolor='#f5f5f5', 
                edgecolor='#666666', alpha=0.9, linewidth=1)
    ax.text(0.98, 0.02, analysis_text, transform=ax.transAxes, fontsize=9,
           verticalalignment='bottom', horizontalalignment='right', 
           bbox=props, family='monospace')
    
    plt.tight_layout()
    plt.show()


def plot_signal_integrity_timeline(gps_path, spoof_flags, timestamps=None):
    """
    Generates temporal analysis of GNSS signal integrity status.
    
    Parameters:
    gps_path: List of position data points
    spoof_flags: List of signal integrity flags
    timestamps: Optional list of timestamp values
    """
    if not timestamps:
        timestamps = list(range(len(gps_path)))
    
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor('white')
    
    # Signal integrity status mapping
    integrity_values = [0 if not spoofed else 1 for spoofed in spoof_flags]
    colors = ['#2e7d32' if not spoofed else '#d32f2f' for spoofed in spoof_flags]
    labels = ['VERIFIED' if not spoofed else 'COMPROMISED' for spoofed in spoof_flags]
    
    # Plot integrity status over time
    ax.scatter(timestamps, integrity_values, c=colors, s=150, alpha=0.8, 
              edgecolors='black', linewidth=1, zorder=3)
    
    # Add status annotations
    for i, (t, label, color) in enumerate(zip(timestamps, labels, colors)):
        ax.annotate(f'T{i}: {label}', (t, integrity_values[i]), 
                   xytext=(0, 25), textcoords='offset points', 
                   ha='center', fontsize=9, fontweight='bold', 
                   color=color, bbox=dict(boxstyle="round,pad=0.3", 
                   facecolor='white', edgecolor=color, alpha=0.8))
    
    # Configure timeline visualization
    ax.set_ylim(-0.5, 1.5)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['VERIFIED', 'COMPROMISED'])
    ax.set_xlabel('Temporal Sequence', fontsize=12, fontweight='bold')
    ax.set_ylabel('Signal Integrity Status', fontsize=12, fontweight='bold')
    ax.set_title('GNSS Signal Integrity Temporal Analysis', 
                fontsize=14, fontweight='bold')
    
    # Add background regions for clarity
    ax.axhspan(-0.5, 0.5, alpha=0.1, color='green', label='Verified Signal Zone')
    ax.axhspan(0.5, 1.5, alpha=0.1, color='red', label='Compromised Signal Zone')
    
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', framealpha=0.9)
    
    plt.tight_layout()
    plt.show()


def generate_navigation_report(gps_path, fallback_path, spoof_flags):
    """
    Generates comprehensive navigation system performance report.
    
    Returns:
    dict: System performance metrics and analysis summary
    """
    if not gps_path or not spoof_flags:
        return {"error": "Insufficient data for analysis"}
    
    total_points = len(gps_path)
    compromised_count = sum(spoof_flags)
    verified_count = total_points - compromised_count
    
    integrity_ratio = (verified_count / total_points) * 100
    threat_detection_rate = (compromised_count / total_points) * 100
    
    fallback_utilization = 0
    if fallback_path:
        fallback_utilization = sum(1 for fp in fallback_path if fp is not None)
    
    report = {
        "mission_summary": {
            "total_navigation_points": total_points,
            "verified_gnss_positions": verified_count,
            "compromised_signals_detected": compromised_count,
            "signal_integrity_ratio": f"{integrity_ratio:.1f}%",
            "threat_detection_rate": f"{threat_detection_rate:.1f}%"
        },
        "system_performance": {
            "fallback_activations": fallback_utilization,
            "navigation_continuity": "MAINTAINED" if fallback_utilization > 0 else "NOMINAL",
            "threat_mitigation": "SUCCESSFUL" if compromised_count > 0 else "NOT_REQUIRED"
        },
        "recommendations": []
    }
    
    if threat_detection_rate > 25:
        report["recommendations"].append("HIGH_THREAT_ENVIRONMENT_DETECTED")
    if integrity_ratio < 75:
        report["recommendations"].append("ENHANCED_MONITORING_RECOMMENDED")
    if fallback_utilization == 0 and compromised_count > 0:
        report["recommendations"].append("FALLBACK_SYSTEM_VERIFICATION_REQUIRED")
    
    return report