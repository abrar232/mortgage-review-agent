import logging
logging.basicConfig(level=logging.INFO)

from monitoring.cloudwatch import track_application_review, put_metric, log_application_event

# Test 1: Track a completed review
print("Sending application review metrics...")
track_application_review(
    application_id="MRA-2024-00847",
    compliance_result="PASS",
    confidence=0.9,
    duration_seconds=12.4,
)
print("Done")

# Test 2: Send a custom metric
print("\nSending custom metric...")
put_metric("TestMetric", 1.0)
print("Done")

# Test 3: Log an event
print("\nLogging application event...")
log_application_event(
    application_id="MRA-2024-00847",
    event="TEST_EVENT",
    details={"message": "CloudWatch integration test"},
)
print("Done")