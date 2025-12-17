import importlib
import importlib.metadata
import sys
import os
from azure.ai.anomalydetector import AnomalyDetectorClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.anomalydetector.models import TimeSeriesPoint, DetectRequest

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

# Anomaly detection demo
print('\n--- Anomaly Detection Demo ---')
endpoint = os.environ.get('ANOMALY_DETECTOR_ENDPOINT')
key = os.environ.get('ANOMALY_DETECTOR_KEY')

if not endpoint or not key:
    print('Please set the environment variables:')
    print('$env:ANOMALY_DETECTOR_ENDPOINT = "https://your-resource.cognitiveservices.azure.com/"')
    print('$env:ANOMALY_DETECTOR_KEY = "your-key"')
    sys.exit(1)

client = AnomalyDetectorClient(endpoint, AzureKeyCredential(key))

# Sample time series data
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
    anomalies = [i for i, is_anomaly in enumerate(response.is_anomaly) if is_anomaly]
    print(f'Found {len(anomalies)} anomalies at indices: {anomalies}')
    for i in anomalies:
        print(f'Point {i}: {series[i].value} at {series[i].timestamp}')
except Exception as e:
    print('Error detecting anomalies:', e)

sys.exit(0)

ad_client = AnomalyDetectorClient(ANOMALY_DETECTOR_ENDPOINT, AzureKeyCredential(SUBSCRIPTION_KEY))

time_format = "%Y-%m-%dT%H:%M:%SZ"
blob_url = "Path-to-sample-file-in-your-storage-account"  # example path: https://docstest001.blob.core.windows.net/test/sample_data_5_3000.csv

train_body = ModelInfo(
    data_source=blob_url,
    start_time=datetime.strptime("2021-01-02T00:00:00Z", time_format),
    end_time=datetime.strptime("2021-01-02T05:00:00Z", time_format),
    data_schema="OneTable",
    display_name="sample",
    sliding_window=200,
    align_policy=AlignPolicy(
        align_mode=AlignMode.OUTER,
        fill_n_a_method=FillNAMethod.LINEAR,
        padding_value=0,
    ),
)

batch_inference_body = MultivariateBatchDetectionOptions(
       data_source=blob_url,
       top_contributor_count=10,
       start_time=datetime.strptime("2021-01-02T00:00:00Z", time_format),
       end_time=datetime.strptime("2021-01-02T05:00:00Z", time_format),
   )


print("Training new model...(it may take a few minutes)")
model = ad_client.train_multivariate_model(train_body)
model_id = model.model_id
print("Training model id is {}".format(model_id))

## Wait until the model is ready. It usually takes several minutes
model_status = None
model = None

while model_status != ModelStatus.READY and model_status != ModelStatus.FAILED:
    model = ad_client.get_multivariate_model(model_id)
    print(model)
    model_status = model.model_info.status
    print("Model is {}".format(model_status))
    time.sleep(30)
if model_status == ModelStatus.READY:
    print("Done.\n--------------------")
    # Return the latest model id

# Detect anomaly in the same data source (but a different interval)
result = ad_client.detect_multivariate_batch_anomaly(model_id, batch_inference_body)
result_id = result.result_id

# Get results (may need a few seconds)
anomaly_results = ad_client.get_multivariate_batch_detection_result(result_id)
print("Get detection result...(it may take a few seconds)")

while anomaly_results.summary.status != MultivariateBatchDetectionStatus.READY and anomaly_results.summary.status != MultivariateBatchDetectionStatus.FAILED:
    anomaly_results = ad_client.get_multivariate_batch_detection_result(result_id)
    print("Detection is {}".format(anomaly_results.summary.status))
    time.sleep(5)
    
   
print("Result ID:\t", anomaly_results.result_id)
print("Result status:\t", anomaly_results.summary.status)
print("Result length:\t", len(anomaly_results.results))

# See detailed inference result
for r in anomaly_results.results:
    print(
        "timestamp: {}, is_anomaly: {:<5}, anomaly score: {:.4f}, severity: {:.4f}, contributor count: {:<4d}".format(
            r.timestamp,
            r.value.is_anomaly,
            r.value.score,
            r.value.severity,
            len(r.value.interpretation) if r.value.is_anomaly else 0,
        )
    )
    if r.value.interpretation:
        for contributor in r.value.interpretation:
            print(
                "\tcontributor variable: {:<10}, contributor score: {:.4f}".format(
                    contributor.variable, contributor.contribution_score
                )
            )