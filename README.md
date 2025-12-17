This workspace contains a multivariate anomaly detection demo using `azure.ai.anomalydetector`.

Files:
- `smoke_anomalydetector.py`: Trains a multivariate model on local CSV data and detects anomalies.
- `sample_data_5_3000.csv`: Sample multivariate time series data.

How to run:

1. Replace placeholders in `smoke_anomalydetector.py`:
   - `SUBSCRIPTION_KEY = "YOUR_API_KEY"`
   - `ANOMALY_DETECTOR_ENDPOINT = "YOUR_ENDPOINT"`

2. Run:
   ```powershell
   python smoke_anomalydetector.py
   ```

Note: Training may take several minutes. Ensure your Azure resource supports multivariate anomaly detection.

Notes:
- Python 3.12.10 and `py` launcher installed via `winget`.
- `pip` upgraded to 25.3, `azure.ai.anomalydetector` and `pandas` installed.