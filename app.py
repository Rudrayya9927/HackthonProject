
# app.py
import os
import time
import webbrowser
from threading import Timer
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd
from flask import Flask, render_template, jsonify

# --------- Types ----------
@dataclass
class TimeSeriesPoint:
    timestamp: str
    value: float

# --------- Detector (Z-score) ----------
def detect_entire_series(series: List[TimeSeriesPoint], z_thresh: float = 3.0, window: int = 30):
    values = np.array([pt.value for pt in series], dtype=float)
    s = pd.Series(values)

    minp = max(5, window // 3)
    mean = s.rolling(window, min_periods=minp).mean()
    std = s.rolling(window, min_periods=minp).std(ddof=0)

    global_mean = np.nanmean(values)
    global_std = np.nanstd(values) if np.nanstd(values) > 0 else 1e-6
    z = ((s - mean) / std).fillna((s - global_mean) / global_std)

    is_anomaly = z.abs().gt(z_thresh).tolist()

    vis_mean = mean.fillna(global_mean).to_list()
    vis_upper = (mean + z_thresh * std).fillna(global_mean + z_thresh * global_std).to_list()
    vis_lower = (mean - z_thresh * std).fillna(global_mean - z_thresh * global_std).to_list()

    return {
        "is_anomaly": is_anomaly,
        "z_scores": z.abs().to_list(),
        "mean": vis_mean,
        "upper": vis_upper,
        "lower": vis_lower
    }

# --------- Flask app ----------
app = Flask(__name__)

CSV_PATH = os.getenv("CSV_PATH", "sample_data_5_3000.csv")

def load_series(csv_path: str, ts_col="timestamp", val_col="series_0"):
    df = pd.read_csv(csv_path)
    # Normalize timestamps
    ts = pd.to_datetime(df[ts_col], errors="coerce")
    df[ts_col] = ts.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    series = [TimeSeriesPoint(timestamp=row[ts_col], value=float(row[val_col])) for _, row in df.iterrows()]
    return df, series

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/data")
def api_data():
    df, series = load_series(CSV_PATH)
    det = detect_entire_series(series, z_thresh=3.0, window=30)

    timestamps = df["timestamp"].tolist()
    values = df["series_0"].astype(float).tolist()
    anomalies_idx = [i for i, flag in enumerate(det["is_anomaly"]) if flag]

    payload = {
        "timestamps": timestamps,
        "values": values,
        "is_anomaly": det["is_anomaly"],
        "anomaly_indices": anomalies_idx,
        "mean": det["mean"],
        "upper": det["upper"],
        "lower": det["lower"]
    }
    return jsonify(payload)

def open_browser():
    time.sleep(1)
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Auto-open default browser
    Timer(1.0, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=True)
