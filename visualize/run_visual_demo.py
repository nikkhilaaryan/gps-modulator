#!/usr/bin/env python3
"""
Defense-Grade GPS Spoofing Detection Visualization Demo
Simulates an autonomous drone navigation system responding to a GPS spoofing attack.
"""

import matplotlib.pyplot as plt
import os
from .path_plotter import plot_spoofing_scenario, create_demo_scenario

def print_scenario_explanation():
    """Print a concise explanation of the visualization."""
    print("\n=== GPS Spoofing Scenario Explanation ===")
    print("""
This visualization demonstrates a defense-grade autonomous drone navigation system responding to a GPS spoofing attack:

- True Path (Green Solid Line): The planned route the drone should follow.
- Spoofed GPS (Red Dotted Line): False positions reported during the attack, deviating up to 100m.
- IMU-Corrected Path (Green Dashed Line): Path maintained by IMU and sensor fusion, staying within 10m of the true path.
- Spoofing Zone (Red Shaded Area): Region of maximum deviation during the attack.

The system detects the attack and maintains navigation integrity using IMU-based corrections.
""")
    print("=======================================")

def main():
    """Main function to run the GPS spoofing visualization demo."""
    print("=== Starting GPS Spoofing Visualization Demo ===")

    # Create the scenario
    original, spoofed, corrected, attack_start, attack_end = create_demo_scenario()
    
    print(f"Scenario created:")
    print(f"  - Total waypoints: {len(original)}")
    print(f"  - Attack duration: Points {attack_start} to {attack_end}")
    print(f"  - Attack coverage: {((attack_end - attack_start + 1) / len(original) * 100):.1f}% of route")

    # Create output directory
    os.makedirs('output', exist_ok=True)

    # Generate visualization
    print("\nCreating visualization...")
    fig = plot_spoofing_scenario(
        original_path=original,
        spoofed_gps_path=spoofed,
        corrected_path=corrected,
        spoof_start_idx=attack_start,
        spoof_end_idx=attack_end,
        save_path='output/gps_spoofing_defense.png'
    )

    # Print explanation
    print_scenario_explanation()

    print("\nFile saved: output/gps_spoofing_defense.png")
    print("Close the plot window to exit.")
    plt.show()
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    main()