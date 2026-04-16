print("STARTING EXTRACTION EVAL")

"""
Evaluation: Entity Extraction Agent
Tests whether the extraction agent correctly identifies key fields
from each document type against known ground truth values.
"""

from ingestion.document_parser import parse_document
from agents.extraction_agent import extract_entities

# Ground truth — what we know the documents contain
GROUND_TRUTH = {
    "samples/income_statement.docx": {
        "applicant_name": "James Arthur Whitfield",
        "date_of_birth": "14 March 1988",
        "annual_income": "£72,700",
        "application_reference": "MRA-2024-00847",
        "raw_document_type": "income_statement",
    },
    "samples/affordability_assessment.docx": {
        "loan_amount": "£307,000",
        "purchase_price": "£385,000",
        "ltv_ratio": "79.7%",
        "stress_test_result": "PASS",
        "property_address": "42 Elmwood Drive, Birmingham, B15 3TN",
        "application_reference": "MRA-2024-00847",
        "raw_document_type": "affordability_assessment",
    },
    "samples/id_verification.docx": {
        "applicant_name": "James Arthur Whitfield",
        "date_of_birth": "14 March 1988",
        "id_verification_status": "PASS",
        "application_reference": "MRA-2024-00847",
        "raw_document_type": "id_verification",
    },
}


def normalise(value: str) -> str:
    """Normalise values for comparison — lowercase, strip whitespace."""
    return value.strip().lower()


def run_extraction_eval():
    from evaluations.eval_logger import save_eval_results

    print("=" * 60)
    print("EXTRACTION AGENT EVALUATION")
    print("=" * 60)

    total = 0
    passed = 0
    cases = []

    for doc_path, expected_fields in GROUND_TRUTH.items():
        print(f"\nDocument: {doc_path}")
        parsed = parse_document(doc_path)
        entities = extract_entities(parsed)
        extracted = vars(entities)

        for field, expected_value in expected_fields.items():
            total += 1
            actual_value = extracted.get(field, "NOT_FOUND")
            correct = normalise(actual_value) == normalise(expected_value)

            if correct:
                passed += 1
                print(f"  ✓ {field}: {actual_value}")
            else:
                print(f"  ✗ {field}")
                print(f"      Expected: {expected_value}")
                print(f"      Actual:   {actual_value}")

            cases.append({
                "document": doc_path,
                "field": field,
                "expected": expected_value,
                "actual": actual_value,
                "passed": correct,
            })

    accuracy = round(passed / total * 100, 1)
    print(f"\n{'=' * 60}")
    print(f"EXTRACTION RESULTS: {passed}/{total} fields correct ({accuracy}%)")
    print("=" * 60)

    save_eval_results("extraction", {
        "summary": {"passed": passed, "total": total, "accuracy_pct": accuracy},
        "cases": cases,
    })

    return passed, total


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.WARNING)
    run_extraction_eval()