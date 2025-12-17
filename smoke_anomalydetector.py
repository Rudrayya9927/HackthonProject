
import pandas as pd
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.anomalydetector.models import TimeSeriesPoint, DetectRequest

# Replace with your subscription key and endpoint
SUBSCRIPTION_KEY = "YOUR_API_KEY"
ANOMALY_DETECTOR_ENDPOINT = "YOUR_ENDPOINT"

ad_client = AnomalyDetectorClient(ANOMALY_DETECTOR_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))

# Load local CSV file
csv_path = "sample_data_5_3000.csv"
df = pd.read_csv(csv_path)

# Use the first series for univariate detection
series = []
for index, row in df.iterrows():
    timestamp = row['timestamp']
    value = float(row['series_0'])  # Use series_0
    series.append(TimeSeriesPoint(timestamp=timestamp, value=value))

# Create request
request = DetectRequest(series=series, granularity="daily")

# Detect anomalies
print("Detecting anomalies...")
try:
    response = ad_client.detect_entire_series(request)
    print('Anomaly detection results:')
    anomalies = [i for i, is_anomaly in enumerate(response.is_anomaly) if is_anomaly]
    print(f'Found {len(anomalies)} anomalies')
    for i in anomalies:
        print(f'Point {i}: {series[i].value} at {series[i].timestamp}')
except Exception as e:
    print('Error:', e)
