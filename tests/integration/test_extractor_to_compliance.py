"""
Integration tests: Extraction Agent -> Compliance Check
Tests that extracted entities flow correctly into the compliance node.
"""

import pytest
from unittest.mock import patch
from ingestion.document_parser import parse_document
from agents.extraction_agent import extract_entities
from agents.orchestrator import compliance_check_node


@pytest.fixture(scope="module")
def merged_entities():
    """Merge entities from all three documents as the orchestrator would."""
    docs = [
        "samples/income_statement.docx",
        "samples/affordability_assessment.docx",
        "samples/id_verification.docx",
    ]
    merged = {}
    for path in docs:
        entities = extract_entities(parse_document(path))
        for field, value in vars(entities).items():
            if value != "NOT_FOUND" or field not in merged:
                merged[field] = value
    return merged


@pytest.fixture
def good_credit():
    return {"overall_recommendation": "APPROVE", "adverse_credit_found": False}


@pytest.fixture
def decline_credit():
    return {"overall_recommendation": "DECLINE", "adverse_credit_found": True}


def run_check(entities, credit):
    state = {
        "application_id": "INT-TEST",
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
    with patch("agents.orchestrator.send_compliance_event"):
        return compliance_check_node(state)


class TestMergedEntitiesCompliance:

    def test_full_document_set_passes_compliance(self, merged_entities, good_credit):
        result = run_check(merged_entities, good_credit)
        assert result["compliance_result"] == "PASS"

    def test_full_document_set_no_human_review(self, merged_entities, good_credit):
        result = run_check(merged_entities, good_credit)
        assert result["requires_human_review"] == False

    def test_full_document_set_high_confidence(self, merged_entities, good_credit):
        result = run_check(merged_entities, good_credit)
        assert result["confidence_score"] >= 0.75

    def test_compliance_reasons_reference_real_data(self, merged_entities, good_credit):
        result = run_check(merged_entities, good_credit)
        reasons = result["compliance_reasons"]
        assert any("ID verification" in r for r in reasons)
        assert any("stress test" in r.lower() for r in reasons)
        assert any("LTV" in r for r in reasons)


class TestCreditBureauImpact:

    def test_credit_decline_overrides_good_documents(self, merged_entities, decline_credit):
        result = run_check(merged_entities, decline_credit)
        assert result["compliance_result"] == "FAIL"
        assert result["requires_human_review"] == True

    def test_good_credit_does_not_override_bad_id(self, good_credit):
        bad_id_entities = {
            "id_verification_status": "FAIL",
            "stress_test_result": "PASS",
            "ltv_ratio": "75%",
        }
        result = run_check(bad_id_entities, good_credit)
        assert result["compliance_result"] == "FAIL"

    def test_confidence_higher_with_approve_vs_refer(self, merged_entities):
        approve_result = run_check(
            merged_entities,
            {"overall_recommendation": "APPROVE", "adverse_credit_found": False}
        )
        refer_result = run_check(
            merged_entities,
            {"overall_recommendation": "REFER", "adverse_credit_found": True}
        )
        assert approve_result["confidence_score"] > refer_result["confidence_score"]


class TestMissingDocumentImpact:

    def test_missing_id_doc_reduces_confidence(self, good_credit):
        no_id_entities = {
            "id_verification_status": "NOT_FOUND",
            "stress_test_result": "PASS",
            "ltv_ratio": "75%",
        }
        result = run_check(no_id_entities, good_credit)
        assert result["confidence_score"] < 1.0

    def test_missing_all_docs_fails(self):
        empty_entities = {
            "id_verification_status": "NOT_FOUND",
            "stress_test_result": "NOT_FOUND",
            "ltv_ratio": "NOT_FOUND",
        }
        result = run_check(empty_entities, None)
        assert result["requires_human_review"] == True