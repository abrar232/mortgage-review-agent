"""
Evaluation: End-to-End Pipeline
Runs multiple different application scenarios through the full pipeline
and verifies the correct outcome comes out the other end.
"""

from unittest.mock import patch
from agents.orchestrator import run_application_review
from evaluations.eval_logger import save_eval_results


TEST_CASES = [
    {
        "description": "Standard application — all documents present, should PASS",
        "application_id": "E2E-TEST-001",
        "document_paths": [
            "samples/income_statement.docx",
            "samples/affordability_assessment.docx",
            "samples/id_verification.docx",
        ],
        "expected_result": "PASS",
        "expected_human_review": False,
    },
    {
        "description": "Missing ID document — should ESCALATE",
        "application_id": "E2E-TEST-002",
        "document_paths": [
            "samples/income_statement.docx",
            "samples/affordability_assessment.docx",
        ],
        "expected_result": "ESCALATE",
        "expected_human_review": True,
    },
    {
        "description": "Only income statement — most fields missing, should ESCALATE or FAIL",
        "application_id": "E2E-TEST-003",
        "document_paths": [
            "samples/income_statement.docx",
        ],
        "expected_result": "ESCALATE",
        "expected_human_review": True,
    },
]


def run_end_to_end_eval():
    print("=" * 60)
    print("END-TO-END PIPELINE EVALUATION")
    print("=" * 60)

    total = len(TEST_CASES)
    passed = 0
    cases = []

    for case in TEST_CASES:
        print(f"\nTest: {case['description']}")
        print(f"Application ID: {case['application_id']}")

        # Mock SQS, DynamoDB and CloudWatch so we don't pollute real AWS with test data
        with patch("agents.orchestrator.send_compliance_event"), \
             patch("agents.orchestrator.send_handoff_event"), \
             patch("agents.orchestrator.save_application_state"), \
             patch("agents.orchestrator.track_application_review"):

            result = run_application_review(
                application_id=case["application_id"],
                document_paths=case["document_paths"],
            )

        actual_result = result.get("compliance_result")
        actual_human = result.get("requires_human_review")
        expected_result = case["expected_result"]
        expected_human = case["expected_human_review"]

        # For ESCALATE/FAIL we allow either since both require human review
        if expected_result in ("ESCALATE", "FAIL"):
            correct = actual_human == True
        else:
            correct = actual_result == expected_result and actual_human == expected_human

        if correct:
            passed += 1
            print(f"  ✓ Result: {actual_result} | Human review: {actual_human} | Confidence: {result.get('confidence_score')}")
        else:
            print(f"  ✗ Result: {actual_result} | Human review: {actual_human} | Confidence: {result.get('confidence_score')}")
            print(f"     Expected result={expected_result}, human_review={expected_human}")

        print(f"  Reasons:")
        for r in result.get("compliance_reasons", []):
            print(f"    {r}")

        cases.append({
            "description": case["description"],
            "application_id": case["application_id"],
            "documents": case["document_paths"],
            "expected_result": expected_result,
            "actual_result": actual_result,
            "expected_human_review": expected_human,
            "actual_human_review": actual_human,
            "confidence_score": result.get("confidence_score"),
            "compliance_reasons": result.get("compliance_reasons", []),
            "passed": correct,
        })

    accuracy = round(passed / total * 100, 1)
    print(f"\n{'=' * 60}")
    print(f"END-TO-END RESULTS: {passed}/{total} cases correct ({accuracy}%)")
    print("=" * 60)

    save_eval_results("end_to_end", {
        "summary": {"passed": passed, "total": total, "accuracy_pct": accuracy},
        "cases": cases,
    })

    return passed, total


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.WARNING)
    run_end_to_end_eval()