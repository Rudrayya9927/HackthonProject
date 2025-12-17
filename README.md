This workspace contains a smoke test and demo for `azure.ai.anomalydetector`.

Files:
- `smoke_anomalydetector.py`: Imports the package, shows version, and runs a demo anomaly detection on sample data.

How to run:

1. Set up Azure Anomaly Detector:
   - Create an Azure Cognitive Services resource.
   - Get the endpoint and key from the Azure portal.

2. Set environment variables:
   ```powershell
   $env:ANOMALY_DETECTOR_ENDPOINT="https://your-resource.cognitiveservices.azure.com/"
   $env:ANOMALY_DETECTOR_KEY="your-key"
   ```

3. Run the script:
   ```powershell
   py -3 .\smoke_anomalydetector.py
   ```

Notes:
- Python 3.12.10 and `py` launcher installed via `winget`.
- `pip` upgraded to 25.3 and `azure.ai.anomalydetector` installed (v3.0.0b6).