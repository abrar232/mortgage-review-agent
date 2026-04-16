import json
import logging
import urllib.parse
from dataclasses import asdict

import boto3

from ingestion.document_parser import parse_document

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")


def download_from_s3(bucket: str, key: str, local_path: str) -> None:
    logger.info(f"Downloading s3://{bucket}/{key} to {local_path}")
    s3_client.download_file(bucket, key, local_path)


def handler(event: dict, context) -> dict:
    """
    Entry point for AWS Lambda.
    Triggered by S3 upload events.
    """
    records = event.get("Records", [])
    results = []

    for record in records:
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        logger.info(f"Processing document: s3://{bucket}/{key}")

        # Determine file extension from the S3 key
        if not (key.endswith(".pdf") or key.endswith(".docx")):
            logger.warning(f"Skipping unsupported file type: {key}")
            continue

        # Download to Lambda's ephemeral storage (/tmp is the only writable dir)
        local_path = f"/tmp/{key.split('/')[-1]}"
        download_from_s3(bucket, key, local_path)

        # Parse the document
        parsed = parse_document(local_path)

        logger.info(
            f"Successfully parsed | file={parsed.file_name} "
            f"pages={parsed.page_count} chars={len(parsed.raw_text)}"
        )

        results.append(asdict(parsed))

    return {
        "statusCode": 200,
        "body": json.dumps({"processed": len(results), "documents": results}),
    }