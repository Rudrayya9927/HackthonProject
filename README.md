This workspace contains a local anomaly detection demo using Z-score method on CSV data with visualization.

Files:
- `smoke_anomalydetector.py`: Loads CSV data, detects anomalies, and plots the results.
- `sample_data_5_3000.csv`: Sample time series data.

How to run:

```powershell
python smoke_anomalydetector.py
```

It saves a plot as `anomalies_plot.png`.

Notes:
- Python 3.12.10 installed.
- pandas, numpy, matplotlib installed.