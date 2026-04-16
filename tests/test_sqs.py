import logging
logging.basicConfig(level=logging.INFO)

from config.settings import get_settings
from messaging.sqs import (
    send_ingestion_event,
    send_compliance_event,
    send_handoff_event,
    receive_messages,
    delete_message,
)

settings = get_settings()

# Test 1: Send an ingestion event
print("Sending ingestion event...")
msg_id = send_ingestion_event(
    application_id="MRA-2024-00847",
    document_keys=["applications/income_statement.docx", "applications/affordability_assessment.docx"]
)
print(f"Sent message ID: {msg_id}")

# Test 2: Receive it back
print("\nReceiving from ingestion queue...")
messages = receive_messages(settings.sqs_ingestion_queue_url)
for msg in messages:
    print(f"Body: {msg['body']}")
    delete_message(settings.sqs_ingestion_queue_url, msg["receipt_handle"])
    print("Deleted message after processing")

# Test 3: Send a handoff event
print("\nSending handoff event...")
msg_id = send_handoff_event(
    application_id="MRA-2024-00999",
    reason="LTV exceeds 85% — requires manual underwriting review",
    confidence=0.6,
)
print(f"Sent handoff message ID: {msg_id}")

# Test 4: Receive handoff
print("\nReceiving from handoff queue...")
messages = receive_messages(settings.sqs_handoff_queue_url)
for msg in messages:
    print(f"Body: {msg['body']}")
    delete_message(settings.sqs_handoff_queue_url, msg["receipt_handle"])
    print("Deleted message after processing")