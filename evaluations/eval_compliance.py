"""
Evaluation: Compliance Logic
Tests edge cases through the compliance check node directly
to verify correct outcomes for different application scenarios.
"""

from agents.orchestrator import compliance_check_node
from state.schema import ApplicationState


def make_state(application_id: str, entities: dict, credit_report: dict) -> ApplicationState:
    return {
        "application_id": application_id,
        "document_paths": [],
        "extracted_entities": entities,
        "credit_report": credit_report,
        "policy_clauses": [],
        "compliance_result": None,
        "compliance_reasons": None,
        "confidence_score": None,
        "requires_human_review": False,
        "handoff_reason": None,
        "errors": [],
        "current_step": "compliance",
    }


GOOD_CREDIT = {
    "overall_recommendation": "APPROVE",
    "adverse_credit_found": False,
}

REFER_CREDIT = {
    "overall_recommendation": "REFER",
    "adverse_credit_found": True,
}

DECLINE_CREDIT = {
    "overall_recommendation": "DECLINE",
    "adverse_credit_found": True,
}

TEST_CASES = [
    {
        "description": "All checks pass — should be PASS, no human review",
        "entities": {
            "id_verification_status": "PASS",
            "stress_test_result": "PASS",
            "ltv_ratio": "75%",
        },
        "credit": GOOD_CREDIT,
        "expected_result": "PASS",
        "expected_human_review": False,
    },
    {
        "description": "High LTV (88%) — should ESCALATE to human",
        "entities": {
            "id_verification_status": "PASS",
            "stress_test_result": "PASS",
            "ltv_ratio": "88%",
        },
        "credit": GOOD_CREDIT,
        "expected_result": "ESCALATE",
        "expected_human_review": True,
    },
    {
        "description": "Failed stress test — should ESCALATE or FAIL",
        "entities": {
            "id_verification_status": "PASS",
            "stress_test_result": "FAIL",
            "ltv_ratio": "75%",
        },
        "credit": GOOD_CREDIT,
        "expected_result": "ESCALATE",
        "expected_human_review": True,
    },
    {
        "description": "Failed ID verification — should FAIL",
        "entities": {
            "id_verification_status": "FAIL",
            "stress_test_result": "PASS",
            "ltv_ratio": "75%",
        },
        "credit": GOOD_CREDIT,
        "expected_result": "FAIL",
        "expected_human_review": True,
    },
    {
        "description": "Credit bureau decline — should FAIL",
        "entities": {
            "id_verification_status": "PASS",
            "stress_test_result": "PASS",
            "ltv_ratio": "75%",
        },
        "credit": DECLINE_CREDIT,
        "expected_result": "FAIL",
        "expected_human_review": True,
    },
    {
        "description": "Credit bureau refer + adverse credit — should ESCALATE",
        "entities": {
            "id_verification_status": "PASS",
            "stress_test_result": "PASS",
            "ltv_ratio": "75%",
        },
        "credit": REFER_CREDIT,
        "expected_result": "ESCALATE",
        "expected_human_review": True,
    },
    {
        "description": "Missing ID and stress test — should ESCALATE",
        "entities": {
            "id_verification_status": "NOT_FOUND",
            "stress_test_result": "NOT_FOUND",
            "ltv_ratio": "75%",
        },
        "credit": GOOD_CREDIT,
        "expected_result": "ESCALATE",
        "expected_human_review": True,
    },
    {
        "description": "Everything missing — should FAIL",
        "entities": {
            "id_verification_status": "NOT_FOUND",
            "stress_test_result": "NOT_FOUND",
            "ltv_ratio": "NOT_FOUND",
        },
        "credit": None,
        "expected_result": "FAIL",
        "expected_human_review": True,
    },
]


def run_compliance_eval():
    from evaluations.eval_logger import save_eval_results

    print("=" * 60)
    print("COMPLIANCE LOGIC EVALUATION")
    print("=" * 60)

    total = len(TEST_CASES)
    passed = 0
    cases = []

    for i, case in enumerate(TEST_CASES):
        state = make_state(f"TEST-{i+1:03d}", case["entities"], case["credit"])

        from unittest.mock import patch
        with patch("agents.orchestrator.send_compliance_event"):
            result_state = compliance_check_node(state)

        actual_result = result_state["compliance_result"]
        actual_human = result_state["requires_human_review"]
        expected_result = case["expected_result"]
        expected_human = case["expected_human_review"]
        correct = actual_result == expected_result and actual_human == expected_human

        if correct:
            passed += 1
            print(f"  ✓ [{case['description']}]")
            print(f"      Result: {actual_result} | Human review: {actual_human} | Confidence: {result_state['confidence_score']}")
        else:
            print(f"  ✗ [{case['description']}]")
            if actual_result != expected_result:
                print(f"      Result:  expected={expected_result} actual={actual_result}")
            if actual_human != expected_human:
                print(f"      Human:   expected={expected_human} actual={actual_human}")

        cases.append({
            "description": case["description"],
            "expected_result": expected_result,
            "actual_result": actual_result,
            "expected_human_review": expected_human,
            "actual_human_review": actual_human,
            "confidence_score": result_state["confidence_score"],
            "passed": correct,
        })

    accuracy = round(passed / total * 100, 1)
    print(f"\n{'=' * 60}")
    print(f"COMPLIANCE RESULTS: {passed}/{total} cases correct ({accuracy}%)")
    print("=" * 60)

    save_eval_results("compliance", {
        "summary": {"passed": passed, "total": total, "accuracy_pct": accuracy},
        "cases": cases,
    })

    return passed, total


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.WARNING)
    run_compliance_eval()