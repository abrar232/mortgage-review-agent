import json
import logging
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_dynamodb():
    session = boto3.Session()
    return session.resource("dynamodb", region_name=settings.aws_region)


def save_application_state(state: dict) -> None:
    """Save the full application state to DynamoDB."""
    dynamodb = get_dynamodb()
    table = dynamodb.Table(settings.dynamodb_state_table)

    item = {
        "application_id": state["application_id"],
        "current_step": state.get("current_step", "unknown"),
        "compliance_result": state.get("compliance_result", "PENDING"),
        "confidence_score": str(state.get("confidence_score", 0)),
        "requires_human_review": state.get("requires_human_review", False),
        "handoff_reason": state.get("handoff_reason") or "",
        "extracted_entities": json.dumps(state.get("extracted_entities") or {}),
        "compliance_reasons": json.dumps(state.get("compliance_reasons") or []),
        "errors": json.dumps(state.get("errors") or []),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    table.put_item(Item=item)
    logger.info(f"Saved state for application {state['application_id']}")


def get_application_state(application_id: str) -> dict | None:
    """Retrieve application state from DynamoDB."""
    dynamodb = get_dynamodb()
    table = dynamodb.Table(settings.dynamodb_state_table)

    response = table.get_item(Key={"application_id": application_id})
    item = response.get("Item")

    if not item:
        return None

    # Deserialise JSON fields
    item["extracted_entities"] = json.loads(item.get("extracted_entities", "{}"))
    item["compliance_reasons"] = json.loads(item.get("compliance_reasons", "[]"))
    item["errors"] = json.loads(item.get("errors", "[]"))

    return item


def save_conversation_memory(application_id: str, messages: list[dict]) -> None:
    """Save conversation memory for an application."""
    dynamodb = get_dynamodb()
    table = dynamodb.Table(settings.dynamodb_memory_table)

    table.put_item(Item={
        "application_id": application_id,
        "messages": json.dumps(messages),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })
    logger.info(f"Saved memory for application {application_id}")


def get_conversation_memory(application_id: str) -> list[dict]:
    """Retrieve conversation memory for an application."""
    dynamodb = get_dynamodb()
    table = dynamodb.Table(settings.dynamodb_memory_table)

    response = table.get_item(Key={"application_id": application_id})
    item = response.get("Item")

    if not item:
        return []

    return json.loads(item.get("messages", "[]"))