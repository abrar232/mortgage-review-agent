import json
import logging

import boto3

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_sqs_client():
    session = boto3.Session(profile_name="mortgage-dev")
    return session.client("sqs", region_name=settings.aws_region)


def send_message(queue_url: str, message: dict) -> str:
    """Send a message to an SQS queue. Returns the message ID."""
    client = get_sqs_client()

    response = client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message),
    )

    message_id = response["MessageId"]
    logger.info(f"Sent message {message_id} to {queue_url.split('/')[-1]}")
    return message_id


def receive_messages(queue_url: str, max_messages: int = 1) -> list[dict]:
    """Poll a queue for messages. Returns list of parsed message bodies."""
    client = get_sqs_client()

    response = client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=max_messages,
        WaitTimeSeconds=5,
    )

    messages = response.get("Messages", [])
    result = []

    for msg in messages:
        result.append({
            "receipt_handle": msg["ReceiptHandle"],
            "body": json.loads(msg["Body"]),
        })

    logger.info(f"Received {len(result)} message(s) from {queue_url.split('/')[-1]}")
    return result


def delete_message(queue_url: str, receipt_handle: str) -> None:
    """Delete a message from the queue after processing."""
    client = get_sqs_client()
    client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
    logger.info(f"Deleted message from {queue_url.split('/')[-1]}")


def send_ingestion_event(application_id: str, document_keys: list[str]) -> str:
    """Send a new application to the ingestion queue."""
    return send_message(
        settings.sqs_ingestion_queue_url,
        {
            "event_type": "NEW_APPLICATION",
            "application_id": application_id,
            "document_keys": document_keys,
        }
    )


def send_compliance_event(application_id: str, compliance_result: str, confidence: float) -> str:
    """Send compliance result to the compliance queue."""
    return send_message(
        settings.sqs_compliance_queue_url,
        {
            "event_type": "COMPLIANCE_RESULT",
            "application_id": application_id,
            "compliance_result": compliance_result,
            "confidence_score": confidence,
        }
    )


def send_handoff_event(application_id: str, reason: str, confidence: float) -> str:
    """Send escalation event to the handoff queue for human reviewers."""
    return send_message(
        settings.sqs_handoff_queue_url,
        {
            "event_type": "HUMAN_REVIEW_REQUIRED",
            "application_id": application_id,
            "reason": reason,
            "confidence_score": confidence,
        }
    )