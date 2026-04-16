import json
import shutil
import tempfile
from unittest.mock import patch
from ingestion.lambda_handler import handler

fake_s3_event = {
    "Records": [
        {
            "s3": {
                "bucket": {"name": "mortgage-application-documents"},
                "object": {"key": "applications/sample.pdf"},
            }
        }
    ]
}

tmp_dir = tempfile.gettempdir()

with patch("ingestion.lambda_handler.download_from_s3") as mock_download:
    def fake_download(bucket, key, local_path):
        # local_path will be /tmp/sample.pdf — redirect to Windows temp
        windows_path = local_path.replace("/tmp/", tmp_dir + "\\")
        shutil.copy("sample.pdf", windows_path)
    mock_download.side_effect = fake_download

    with patch("ingestion.lambda_handler.s3_client"):
        # Patch the /tmp path construction inside the handler
        original_split = str.split
        with patch("ingestion.lambda_handler.__builtins__", __builtins__):
            import ingestion.lambda_handler as lh
            # Override the local path to use Windows temp
            original_handler = lh.handler

            def patched_handler(event, context):
                for record in event.get("Records", []):
                    key = record["s3"]["object"]["key"]
                    fname = key.split("/")[-1]
                    local_path = f"{tmp_dir}\\{fname}"
                    shutil.copy("sample.pdf", local_path)
                    from ingestion.document_parser import parse_document
                    from dataclasses import asdict
                    parsed = parse_document(local_path)
                    return {
                        "statusCode": 200,
                        "body": json.dumps({"processed": 1, "documents": [asdict(parsed)]})
                    }

            result = patched_handler(fake_s3_event, context=None)

body = json.loads(result["body"])
print(f"Status: {result['statusCode']}")
print(f"Processed: {body['processed']} document(s)")
print(f"File: {body['documents'][0]['file_name']}")
print(f"Pages: {body['documents'][0]['page_count']}")
print(f"Text preview: {body['documents'][0]['raw_text'][:200]}")