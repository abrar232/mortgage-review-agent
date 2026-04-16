import json
import logging
from dataclasses import dataclass

import anthropic

from config.settings import get_settings
from ingestion.document_parser import ParsedDocument

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ExtractedEntities:
    application_reference: str
    applicant_name: str
    date_of_birth: str
    annual_income: str
    loan_amount: str
    property_address: str
    purchase_price: str
    ltv_ratio: str
    stress_test_result: str
    id_verification_status: str
    raw_document_type: str


def extract_entities(document: ParsedDocument) -> ExtractedEntities:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    prompt = f"""You are a mortgage document analyst for a UK retail bank.

Extract the following fields from the document below. If a field is not present, return "NOT_FOUND".

Fields to extract:
- application_reference
- applicant_name
- date_of_birth
- annual_income
- loan_amount
- property_address
- purchase_price
- ltv_ratio
- stress_test_result
- id_verification_status
- raw_document_type (what type of document is this e.g. income_statement, affordability_assessment, id_verification)

Respond ONLY with a valid JSON object. No explanation, no markdown, just the JSON.

Document:
{document.raw_text}
"""

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    #raw_json = message.content[0].text
    
    #logger.info(f"Raw extraction response: {raw_json}")
    
    raw_json = message.content[0].text
# Strip markdown code fences if model returns them
    raw_json = raw_json.strip()
    if raw_json.startswith("```"):
        raw_json = raw_json.split("\n", 1)[1]  # remove first line (```json)
        raw_json = raw_json.rsplit("```", 1)[0]  # remove closing ```
    raw_json = raw_json.strip()

    data = json.loads(raw_json)

    return ExtractedEntities(
        application_reference=data.get("application_reference", "NOT_FOUND"),
        applicant_name=data.get("applicant_name", "NOT_FOUND"),
        date_of_birth=data.get("date_of_birth", "NOT_FOUND"),
        annual_income=data.get("annual_income", "NOT_FOUND"),
        loan_amount=data.get("loan_amount", "NOT_FOUND"),
        property_address=data.get("property_address", "NOT_FOUND"),
        purchase_price=data.get("purchase_price", "NOT_FOUND"),
        ltv_ratio=data.get("ltv_ratio", "NOT_FOUND"),
        stress_test_result=data.get("stress_test_result", "NOT_FOUND"),
        id_verification_status=data.get("id_verification_status", "NOT_FOUND"),
        raw_document_type=data.get("raw_document_type", "NOT_FOUND"),
    )