This workspace contains a local anomaly detection demo using Z-score method on CSV data.

Files:
- `smoke_anomalydetector.py`: Loads CSV data and detects anomalies using rolling Z-score.
- `sample_data_5_3000.csv`: Sample time series data.

How to run:

```powershell
python smoke_anomalydetector.py
```

It uses local computation, no Azure API required.

Notes:
- Python 3.12.10 installed.
- pandas and numpy installed.