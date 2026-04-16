from ingestion.document_parser import parse_document
from agents.extraction_agent import extract_entities

docs = [
    "samples/income_statement.docx",
    "samples/affordability_assessment.docx",
    "samples/id_verification.docx",
]

for path in docs:
    print(f"\n{'='*50}")
    print(f"Processing: {path}")
    parsed = parse_document(path)
    entities = extract_entities(parsed)
    print(f"Document type:     {entities.raw_document_type}")
    print(f"Application ref:   {entities.application_reference}")
    print(f"Applicant:         {entities.applicant_name}")
    print(f"DOB:               {entities.date_of_birth}")
    print(f"Annual income:     {entities.annual_income}")
    print(f"Loan amount:       {entities.loan_amount}")
    print(f"Property:          {entities.property_address}")
    print(f"Purchase price:    {entities.purchase_price}")
    print(f"LTV:               {entities.ltv_ratio}")
    print(f"Stress test:       {entities.stress_test_result}")
    print(f"ID verification:   {entities.id_verification_status}")