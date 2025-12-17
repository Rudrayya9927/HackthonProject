import importlib
import importlib.metadata
import sys
import os
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.anomalydetector.models import Point, TimeSeriesPoint, DetectRequest

# Smoke test for azure.ai.anomalydetector
try:
    import azure.ai.anomalydetector as ad
    dist_version = importlib.metadata.version('azure-ai-anomalydetector')
    print('Import OK')
    print('Distribution version:', dist_version)
    print('Module repr:', repr(ad))
except Exception as e:
    print('Error importing package:', e)
    sys.exit(1)

# Extra: show interpreter path for clarity
print('Python executable:', sys.executable)
print('Launcher (py) check:')
try:
    import subprocess
    out = subprocess.run(['py','-3','-c','import sys; print(sys.executable)'], capture_output=True, text=True)
    print(out.stdout.strip())
except Exception as e:
    print('py launcher check failed:', e)

# Anomaly detection demo
print('\n--- Anomaly Detection Demo ---')
endpoint = os.getenv('ANOMALY_DETECTOR_ENDPOINT')
key = os.getenv('ANOMALY_DETECTOR_KEY')

if not endpoint or not key:
    print('Set ANOMALY_DETECTOR_ENDPOINT and ANOMALY_DETECTOR_KEY environment variables.')
    print('Example: $env:ANOMALY_DETECTOR_ENDPOINT="https://your-resource.cognitiveservices.azure.com/"')
    print('$env:ANOMALY_DETECTOR_KEY="your-key"')
    sys.exit(1)

client = AnomalyDetectorClient(endpoint, AzureKeyCredential(key))

# Sample time series data (replace with real data)
series = [
    TimeSeriesPoint(timestamp="2021-01-01T00:00:00Z", value=5.0),
    TimeSeriesPoint(timestamp="2021-01-02T00:00:00Z", value=5.1),
    TimeSeriesPoint(timestamp="2021-01-03T00:00:00Z", value=5.2),
    TimeSeriesPoint(timestamp="2021-01-04T00:00:00Z", value=5.0),
    TimeSeriesPoint(timestamp="2021-01-05T00:00:00Z", value=10.0),  # Anomaly
    TimeSeriesPoint(timestamp="2021-01-06T00:00:00Z", value=5.1),
]

request = DetectRequest(series=series, granularity="daily")

try:
    response = client.detect_entire_series(request)
    print('Anomaly detection results:')
    for i, point in enumerate(response.is_anomaly):
        print(f'Point {i}: {"Anomaly" if point else "Normal"}')
except Exception as e:
    print('Error detecting anomalies:', e)

sys.exit(0)

