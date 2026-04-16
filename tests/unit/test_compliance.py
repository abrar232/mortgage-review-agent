"""
Unit tests for the compliance check node.
"""

import pytest
from unittest.mock import patch
from agents.orchestrator import compliance_check_node


def make_state(application_id, entities, credit):
    return {
        "application_id": application_id,
        "document_paths": [],
        "extracted_entities": entities,
        "credit_report": credit,
        "policy_clauses": [],
        "compliance_result": None,
        "compliance_reasons": None,
        "confidence_score": None,
        "requires_human_review": False,
        "handoff_reason": None,
        "errors": [],
        "current_step": "compliance",
    }


GOOD_CREDIT = {"overall_recommendation": "APPROVE", "adverse_credit_found": False}
REFER_CREDIT = {"overall_recommendation": "REFER", "adverse_credit_found": True}
DECLINE_CREDIT = {"overall_recommendation": "DECLINE", "adverse_credit_found": True}


@pytest.fixture
def run_compliance():
    """Helper fixture that runs compliance check with mocked SQS."""
    def _run(entities, credit):
        state = make_state("TEST-001", entities, credit)
        with patch("agents.orchestrator.send_compliance_event"):
            return compliance_check_node(state)
    return _run


class TestCompliancePass:

    def test_all_pass_gives_pass_result(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "PASS", "stress_test_result": "PASS", "ltv_ratio": "75%"},
            GOOD_CREDIT
        )
        assert result["compliance_result"] == "PASS"

    def test_all_pass_no_human_review(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "PASS", "stress_test_result": "PASS", "ltv_ratio": "75%"},
            GOOD_CREDIT
        )
        assert result["requires_human_review"] == False

    def test_all_pass_high_confidence(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "PASS", "stress_test_result": "PASS", "ltv_ratio": "75%"},
            GOOD_CREDIT
        )
        assert result["confidence_score"] >= 0.75

    def test_ltv_at_boundary_80_passes(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "PASS", "stress_test_result": "PASS", "ltv_ratio": "80%"},
            GOOD_CREDIT
        )
        assert result["compliance_result"] == "PASS"


class TestComplianceHardFail:

    def test_id_fail_is_hard_fail(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "FAIL", "stress_test_result": "PASS", "ltv_ratio": "75%"},
            GOOD_CREDIT
        )
        assert result["compliance_result"] == "FAIL"

    def test_id_fail_requires_human_review(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "FAIL", "stress_test_result": "PASS", "ltv_ratio": "75%"},
            GOOD_CREDIT
        )
        assert result["requires_human_review"] == True

    def test_bureau_decline_is_hard_fail(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "PASS", "stress_test_result": "PASS", "ltv_ratio": "75%"},
            DECLINE_CREDIT
        )
        assert result["compliance_result"] == "FAIL"

    def test_both_id_fail_and_decline_is_fail(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "FAIL", "stress_test_result": "FAIL", "ltv_ratio": "95%"},
            DECLINE_CREDIT
        )
        assert result["compliance_result"] == "FAIL"
        assert result["requires_human_review"] == True


class TestComplianceEscalate:

    def test_high_ltv_escalates(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "PASS", "stress_test_result": "PASS", "ltv_ratio": "88%"},
            GOOD_CREDIT
        )
        assert result["requires_human_review"] == True

    def test_bureau_refer_escalates(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "PASS", "stress_test_result": "PASS", "ltv_ratio": "75%"},
            REFER_CREDIT
        )
        assert result["requires_human_review"] == True

    def test_missing_stress_test_reduces_confidence(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "PASS", "stress_test_result": "NOT_FOUND", "ltv_ratio": "75%"},
            GOOD_CREDIT
        )
        assert result["confidence_score"] < 1.0

    def test_missing_id_reduces_confidence(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "NOT_FOUND", "stress_test_result": "PASS", "ltv_ratio": "75%"},
            GOOD_CREDIT
        )
        assert result["confidence_score"] < 1.0


class TestComplianceReasons:

    def test_reasons_list_is_populated(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "PASS", "stress_test_result": "PASS", "ltv_ratio": "75%"},
            GOOD_CREDIT
        )
        assert len(result["compliance_reasons"]) > 0

    def test_pass_reasons_contain_checkmarks(self, run_compliance):
        result = run_compliance(
            {"id_verification_status": "PASS", "stress_test_result": "PASS", "ltv_ratio": "75%"},
            GOOD_CREDIT
        )
        assert any("✓" in r for r in result["compliance_reasons"])


@pytest.mark.parametrize("ltv,expected_human", [
    ("70%", False),
    ("80%", False),
    ("81%", False),
    ("86%", True),
    ("90%", True),
])
def test_ltv_thresholds(ltv, expected_human):
    state = make_state("TEST-LTV", 
        {"id_verification_status": "PASS", "stress_test_result": "PASS", "ltv_ratio": ltv},
        GOOD_CREDIT
    )
    with patch("agents.orchestrator.send_compliance_event"):
        result = compliance_check_node(state)
    assert result["requires_human_review"] == expected_human