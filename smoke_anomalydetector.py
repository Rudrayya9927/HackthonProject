
import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List

# Mimic Azure's TimeSeriesPoint and DetectResponse
@dataclass
class TimeSeriesPoint:
    timestamp: str
    value: float

@dataclass
class DetectResponse:
    is_anomaly: List[bool]

# Simple Z-score based anomaly detection
def detect_entire_series(series: List[TimeSeriesPoint], z_thresh: float = 3.0, window: int = 30) -> DetectResponse:
    values = np.array([pt.value for pt in series])
    s = pd.Series(values)
    mean = s.rolling(window, min_periods=max(5, window // 3)).mean()
    std = s.rolling(window, min_periods=max(5, window // 3)).std(ddof=0)

    # Fallback global stats
    global_mean = np.nanmean(values)
    global_std = np.nanstd(values) if np.nanstd(values) > 0 else 1e-6
    z = ((s - mean) / std).fillna((s - global_mean) / global_std)

    is_anomaly = z.abs().gt(z_thresh).tolist()
    return DetectResponse(is_anomaly=is_anomaly)

# Load local CSV file
csv_path = "sample_data_5_3000.csv"
df = pd.read_csv(csv_path)

# Prepare series
series = [TimeSeriesPoint(timestamp=row['timestamp'], value=float(row['series_0'])) for _, row in df.iterrows()]

# Detect anomalies locally
print("Detecting anomalies (mock, no Azure)...")
response = detect_entire_series(series, z_thresh=3.0, window=30)

# Print results
anomalies = [i for i, is_anomaly in enumerate(response.is_anomaly) if is_anomaly]
print(f"Found {len(anomalies)} anomalies")
for i in anomalies[:20]:  # print top 20 anomalies
    print(f"Point {i}: {series[i].value} at {series[i].timestamp}")
