from ingestion.document_parser import parse_document

for fname in ["income_statement.docx", "affordability_assessment.docx", "id_verification.docx"]:
    result = parse_document(f"samples/{fname}")
    print(f"\n{'='*50}")
    print(f"File: {result.file_name}")
    print(f"Pages/Paragraphs: {result.page_count}")
    print(f"Preview:\n{result.raw_text[:200]}")