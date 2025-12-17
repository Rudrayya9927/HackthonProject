This workspace contains a local anomaly detection demo using Z-score method on CSV data with visualization and web interface.

Files:
- `smoke_anomalydetector.py`: Loads CSV data, detects anomalies, and plots the results.
- `sample_data_5_3000.csv`: Sample time series data.
- `app.py`: Flask web app for interactive dashboard.
- `templates/index.html`: HTML template.
- `static/css/styles.css`: Styles.
- `static/js/app.js`: JavaScript for chart and data fetching.

How to run:

Command line:
```powershell
python smoke_anomalydetector.py
```

Web app:
```powershell
python app.py
```
Then open http://127.0.0.1:5000

Notes:
- Python 3.12.10 installed.
- pandas, numpy, matplotlib, flask installed.