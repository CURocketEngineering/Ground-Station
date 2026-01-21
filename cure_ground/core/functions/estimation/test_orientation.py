"""
Uses simulated data to compare estimated orientation against known orientation.
"""

import pandas as pd
import matplotlib.pyplot as plt

# --- Load CSV ---
df = pd.read_csv(
    r"/Users/randy/Documents/Telemetry Dashboard/data/angular_velocity_deg_100hz.csv"
)

# --- Extract relevant columns ---
t = df["time_s"]
yaw_rate = df["yaw_rate_deg_s"]
pitch_rate = df["pitch_rate_deg_s"]
roll_rate = df["roll_rate_deg_s"]

# --- Plot ---
plt.figure(figsize=(10, 6))
plt.plot(t, yaw_rate, label="Yaw rate (°/s)", color="tab:blue")
plt.plot(t, pitch_rate, label="Pitch rate (°/s)", color="tab:orange")
plt.plot(t, roll_rate, label="Roll rate (°/s)", color="tab:green")

# --- Labels and style ---
plt.title("Yaw, Pitch, and Roll Rates Over Time")
plt.xlabel("Time (s)")
plt.ylabel("Angular Rate (°/s)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()

plt.show()
