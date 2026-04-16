import logging
import time
from datetime import datetime, timezone
from functools import wraps

import boto3

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_cloudwatch_client():
    session = boto3.Session(profile_name="mortgage-dev")
    return session.client("cloudwatch", region_name=settings.aws_region)


def get_logs_client():
    session = boto3.Session(profile_name="mortgage-dev")
    return session.client("logs", region_name=settings.aws_region)


def put_metric(metric_name: str, value: float, unit: str = "Count", dimensions: dict = None) -> None:
    """Send a custom metric to CloudWatch."""
    client = get_cloudwatch_client()

    metric = {
        "MetricName": metric_name,
        "Value": value,
        "Unit": unit,
        "Timestamp": datetime.now(timezone.utc),
    }

    if dimensions:
        metric["Dimensions"] = [
            {"Name": k, "Value": v} for k, v in dimensions.items()
        ]

    client.put_metric_data(
        Namespace=settings.cloudwatch_metrics_namespace,
        MetricData=[metric],
    )

    logger.info(f"CloudWatch metric: {metric_name}={value} {unit}")


def log_application_event(application_id: str, event: str, details: dict = None) -> None:
    """Send a structured log event to CloudWatch Logs."""
    client = get_logs_client()
    log_group = settings.cloudwatch_log_group
    log_stream = f"applications/{application_id}"

    # Create log stream if it doesn't exist
    try:
        client.create_log_stream(
            logGroupName=log_group,
            logStreamName=log_stream,
        )
    except client.exceptions.ResourceAlreadyExistsException:
        pass

    import json
    message = json.dumps({
        "application_id": application_id,
        "event": event,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    client.put_log_events(
        logGroupName=log_group,
        logStreamName=log_stream,
        logEvents=[{
            "timestamp": int(time.time() * 1000),
            "message": message,
        }]
    )

    logger.info(f"CloudWatch log: [{application_id}] {event}")


def track_application_review(application_id: str, compliance_result: str, confidence: float, duration_seconds: float) -> None:
    """Send all metrics for a completed application review."""

    # Metric 1: Total applications processed
    put_metric("ApplicationsProcessed", 1)

    # Metric 2: Compliance result breakdown
    put_metric(f"ComplianceResult_{compliance_result}", 1)

    # Metric 3: Confidence score
    put_metric("ConfidenceScore", confidence, unit="None")

    # Metric 4: Processing time
    put_metric("ReviewDurationSeconds", duration_seconds, unit="Seconds")

    # Metric 5: Human review required
    if compliance_result in ("ESCALATE", "FAIL"):
        put_metric("HumanReviewRequired", 1)

    # Log the event
    log_application_event(
        application_id=application_id,
        event="APPLICATION_REVIEW_COMPLETED",
        details={
            "compliance_result": compliance_result,
            "confidence_score": confidence,
            "duration_seconds": duration_seconds,
        }
    )


def time_it(func):
    """Decorator to measure and log function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = round(time.time() - start, 2)
        logger.info(f"{func.__name__} completed in {duration}s")
        return result
    return wrapper