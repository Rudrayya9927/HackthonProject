This workspace contains a univariate anomaly detection demo using `azure.ai.anomalydetector` with local CSV data.

Files:
- `smoke_anomalydetector.py`: Loads CSV data and detects anomalies in one series.
- `sample_data_5_3000.csv`: Sample multivariate time series data (uses series_0 for demo).

How to run:

1. Replace placeholders in `smoke_anomalydetector.py`:
   - `SUBSCRIPTION_KEY = "YOUR_API_KEY"`
   - `ANOMALY_DETECTOR_ENDPOINT = "YOUR_ENDPOINT"`

2. Run:
   ```powershell
   python smoke_anomalydetector.py
   ```

Notes:
- Python 3.12.10 and `py` launcher installed via `winget`.
- `pip` upgraded to 25.3, `azure.ai.anomalydetector` and `pandas` installed.