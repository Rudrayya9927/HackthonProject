
import time
import pandas as pd
from datetime import datetime
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.anomalydetector.models import *

# Replace with your subscription key and endpoint
SUBSCRIPTION_KEY = "YOUR_API_KEY"
ANOMALY_DETECTOR_ENDPOINT = "YOUR_ENDPOINT"

ad_client = AnomalyDetectorClient(ANOMALY_DETECTOR_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))

# Load local CSV file
csv_path = "sample_data_5_3000.csv"  # Replace with your file path
df = pd.read_csv(csv_path)

# Ensure timestamp column is in ISO format
df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime("%Y-%m-%dT%H:%M:%SZ")

# Prepare multivariate series
series_list = []
for col in df.columns:
    if col != 'timestamp':
        values = [float(v) for v in df[col].tolist()]
        series_list.append(MultivariateSeries(name=col, values=values))

# Create request body
train_body = ModelInfo(
    start_time=datetime.strptime(df['timestamp'].iloc[0], "%Y-%m-%dT%H:%M:%SZ"),
    end_time=datetime.strptime(df['timestamp'].iloc[-1], "%Y-%m-%dT%H:%M:%SZ"),
    sliding_window=200,
    display_name="local_csv_model",
    align_policy=AlignPolicy(
        align_mode=AlignMode.OUTER,
        fill_n_a_method=FillNAMethod.LINEAR,
        padding_value=0,
    ),
    data_schema="OneTable",
    source=series_list
)

# Train model
print("Training new model...(it may take a few minutes)")
model = ad_client.train_multivariate_model(train_body)
model_id = model.model_id
print(f"Training model id: {model_id}")

# Wait until model is ready
model_status = None
while model_status != ModelStatus.READY and model_status != ModelStatus.FAILED:
    model = ad_client.get_multivariate_model(model_id)
    model_status = model.model_info.status
    print(f"Model status: {model_status}")
    time.sleep(30)

if model_status == ModelStatus.READY:
    print("Model training completed.")

# Detect anomalies using same data
batch_inference_body = MultivariateBatchDetectionOptions(
    start_time=datetime.strptime(df['timestamp'].iloc[0], "%Y-%m-%dT%H:%M:%SZ"),
    end_time=datetime.strptime(df['timestamp'].iloc[-1], "%Y-%m-%dT%H:%M:%SZ"),
    top_contributor_count=10,
    source=series_list
)

result = ad_client.detect_multivariate_batch_anomaly(model_id, batch_inference_body)
result_id = result.result_id

# Poll for results
anomaly_results = ad_client.get_multivariate_batch_detection_result(result_id)
while anomaly_results.summary.status != MultivariateBatchDetectionStatus.READY and anomaly_results.summary.status != MultivariateBatchDetectionStatus.FAILED:
    anomaly_results = ad_client.get_multivariate_batch_detection_result(result_id)
    print(f"Detection status: {anomaly_results.summary.status}")
    time.sleep(5)

# Print results
print("Result ID:", anomaly_results.result_id)
for r in anomaly_results.results:
    print(f"timestamp: {r.timestamp}, is_anomaly: {r.value.is_anomaly}, score: {r.value.score:.4f}, severity: {r.value.severity:.4f}")
    if r.value.interpretation:
        for contributor in r.value.interpretation:
            print(f"  Contributor: {contributor.variable}, contribution score: {contributor.contribution_score:.4f}")
