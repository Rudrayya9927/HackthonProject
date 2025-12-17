
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List

# --------- Types ----------
@dataclass
class TimeSeriesPoint:
    timestamp: str
    value: float

@dataclass
class DetectResponse:
    is_anomaly: List[bool]
    z_scores: List[float]            # add z-scores for plotting
    mean: List[float]                # rolling mean (optional to plot)
    upper_band: List[float]          # mean + z_thresh * std
    lower_band: List[float]          # mean - z_thresh * std

# --------- Detector ----------
def detect_entire_series(series: List[TimeSeriesPoint], z_thresh: float = 3.0, window: int = 30) -> DetectResponse:
    values = np.array([pt.value for pt in series], dtype=float)
    s = pd.Series(values)

    # Rolling statistics
    minp = max(5, window // 3)
    mean = s.rolling(window, min_periods=minp).mean()
    std = s.rolling(window, min_periods=minp).std(ddof=0)

    # Fallback global stats
    global_mean = np.nanmean(values)
    global_std = np.nanstd(values) if np.nanstd(values) > 0 else 1e-6
    z = ((s - mean) / std).fillna((s - global_mean) / global_std)

    is_anomaly = z.abs().gt(z_thresh).tolist()

    # Bands for visualization
    vis_mean = mean.fillna(global_mean).to_list()
    vis_upper = (mean + z_thresh * std).fillna(global_mean + z_thresh * global_std).to_list()
    vis_lower = (mean - z_thresh * std).fillna(global_mean - z_thresh * global_std).to_list()

    return DetectResponse(
        is_anomaly=is_anomaly,
        z_scores=z.abs().to_list(),
        mean=vis_mean,
        upper_band=vis_upper,
        lower_band=vis_lower
    )

# --------- Load data ----------
csv_path = "sample_data_5_3000.csv"
df = pd.read_csv(csv_path)

# Prepare series
series = [TimeSeriesPoint(timestamp=row['timestamp'], value=float(row['series_0'])) for _, row in df.iterrows()]

# --------- Detect anomalies ----------
print("Detecting anomalies (mock, no Azure)...")
response = detect_entire_series(series, z_thresh=3.0, window=30)

# Indices of anomalies
anomalies_idx = [i for i, is_anomaly in enumerate(response.is_anomaly) if is_anomaly]
print(f"Found {len(anomalies_idx)} anomalies")
for i in anomalies_idx[:20]:  # keep output short
    print(f"Point {i}: {series[i].value} at {series[i].timestamp}")

# --------- Plot ----------
# Convert timestamps to pandas datetime for nice axis formatting
timestamps = pd.to_datetime([pt.timestamp for pt in series], errors='coerce')

values = np.array([pt.value for pt in series], dtype=float)
mean = np.array(response.mean, dtype=float)
upper = np.array(response.upper_band, dtype=float)
lower = np.array(response.lower_band, dtype=float)

plt.figure(figsize=(12, 6))
plt.plot(timestamps, values, color="#1f77b4", linewidth=1.5, label="series_0")
plt.plot(timestamps, mean, color="#2ca02c", linewidth=1.2, alpha=0.9, label="rolling mean")

# Shaded threshold band
plt.fill_between(timestamps, lower, upper, color="#2ca02c", alpha=0.15, label="± z-threshold band")

# Anomaly points
anom_times = timestamps[anomalies_idx]
anom_vals = values[anomalies_idx]
plt.scatter(anom_times, anom_vals, color="#d62728", s=36, zorder=3, label="anomalies")

# Axis + labels
plt.title("Anomaly Detection (Z-score) – series_0", fontsize=14)
plt.xlabel("Time")
plt.ylabel("Value")
plt.legend(loc="best")
plt.grid(True, alpha=0.25)

# Make dense time labels readable
plt.gcf().autofmt_xdate()

plt.tight_layout()
