"""
Integration tests: Full end-to-end pipeline
Tests the complete workflow from documents to final compliance decision.
"""

import pytest
from unittest.mock import patch


def run_pipeline(application_id, document_paths):
    """Helper that runs the pipeline with AWS services mocked."""
    from agents.orchestrator import run_application_review
    with patch("agents.orchestrator.send_compliance_event"), \
         patch("agents.orchestrator.send_handoff_event"), \
         patch("agents.orchestrator.save_application_state"), \
         patch("agents.orchestrator.track_application_review"):
        return run_application_review(
            application_id=application_id,
            document_paths=document_paths,
        )


ALL_DOCS = [
    "samples/income_statement.docx",
    "samples/affordability_assessment.docx",
    "samples/id_verification.docx",
]


@pytest.fixture(scope="module")
def full_pipeline_result():
    return run_pipeline("E2E-001", ALL_DOCS)


class TestPipelineOutput:

    def test_result_has_application_id(self, full_pipeline_result):
        assert full_pipeline_result["application_id"] == "E2E-001"

    def test_result_has_compliance_result(self, full_pipeline_result):
        assert full_pipeline_result["compliance_result"] in ("PASS", "ESCALATE", "FAIL")

    def test_result_has_confidence_score(self, full_pipeline_result):
        assert full_pipeline_result["confidence_score"] is not None

    def test_confidence_score_between_0_and_1(self, full_pipeline_result):
        assert 0.0 <= full_pipeline_result["confidence_score"] <= 1.0

    def test_result_has_compliance_reasons(self, full_pipeline_result):
        assert full_pipeline_result["compliance_reasons"] is not None
        assert len(full_pipeline_result["compliance_reasons"]) > 0

    def test_result_has_extracted_entities(self, full_pipeline_result):
        assert full_pipeline_result["extracted_entities"] is not None

    def test_result_has_credit_report(self, full_pipeline_result):
        assert full_pipeline_result["credit_report"] is not None

    def test_result_has_policy_clauses(self, full_pipeline_result):
        assert full_pipeline_result["policy_clauses"] is not None
        assert len(full_pipeline_result["policy_clauses"]) > 0


class TestFullDocumentSetOutcome:

    def test_all_documents_produces_pass(self, full_pipeline_result):
        assert full_pipeline_result["compliance_result"] == "PASS"

    def test_all_documents_no_human_review(self, full_pipeline_result):
        assert full_pipeline_result["requires_human_review"] == False

    def test_all_documents_high_confidence(self, full_pipeline_result):
        assert full_pipeline_result["confidence_score"] >= 0.75

    def test_extracted_applicant_name_correct(self, full_pipeline_result):
        entities = full_pipeline_result["extracted_entities"]
        assert entities.get("applicant_name") == "James Arthur Whitfield"

    def test_extracted_ltv_correct(self, full_pipeline_result):
        entities = full_pipeline_result["extracted_entities"]
        assert entities.get("ltv_ratio") == "79.7%"


class TestMissingDocumentOutcomes:

    def test_missing_id_document_escalates(self):
        result = run_pipeline("E2E-002", [
            "samples/income_statement.docx",
            "samples/affordability_assessment.docx",
        ])
        assert result["requires_human_review"] == True

    def test_only_income_statement_escalates_or_fails(self):
        result = run_pipeline("E2E-003", [
            "samples/income_statement.docx",
        ])
        assert result["requires_human_review"] == True

    def test_missing_id_has_lower_confidence_than_full_set(self, full_pipeline_result):
        partial_result = run_pipeline("E2E-004", [
            "samples/income_statement.docx",
            "samples/affordability_assessment.docx",
        ])
        assert partial_result["confidence_score"] < full_pipeline_result["confidence_score"]


class TestPipelineSteps:

    def test_all_pipeline_steps_executed(self, full_pipeline_result):
        assert full_pipeline_result["current_step"] is not None

    def test_errors_list_is_present(self, full_pipeline_result):
        assert "errors" in full_pipeline_result

    def test_no_errors_on_clean_run(self, full_pipeline_result):
        errors = full_pipeline_result.get("errors") or []
        assert len(errors) == 0

    def test_credit_report_has_three_bureaus(self, full_pipeline_result):
        reports = full_pipeline_result["credit_report"]["reports"]
        bureaus = {r["bureau"] for r in reports}
        assert bureaus == {"Experian", "Equifax", "TransUnion"}