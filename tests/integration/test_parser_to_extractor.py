"""
Integration tests: Document Parser -> Extraction Agent
Tests that parser output flows correctly into the extraction agent.
"""

import pytest
from ingestion.document_parser import parse_document
from agents.extraction_agent import extract_entities


@pytest.fixture(scope="module")
def income_entities():
    return extract_entities(parse_document("samples/income_statement.docx"))


@pytest.fixture(scope="module")
def affordability_entities():
    return extract_entities(parse_document("samples/affordability_assessment.docx"))


@pytest.fixture(scope="module")
def id_entities():
    return extract_entities(parse_document("samples/id_verification.docx"))


class TestIncomeStatementExtraction:

    def test_extracts_applicant_name(self, income_entities):
        assert income_entities.applicant_name == "James Arthur Whitfield"

    def test_extracts_application_reference(self, income_entities):
        assert income_entities.application_reference == "MRA-2024-00847"

    def test_extracts_annual_income(self, income_entities):
        assert income_entities.annual_income == "£72,700"

    def test_extracts_date_of_birth(self, income_entities):
        assert income_entities.date_of_birth == "14 March 1988"

    def test_identifies_document_type(self, income_entities):
        assert income_entities.raw_document_type == "income_statement"

    def test_non_present_fields_are_not_found(self, income_entities):
        assert income_entities.loan_amount == "NOT_FOUND"
        assert income_entities.ltv_ratio == "NOT_FOUND"


class TestAffordabilityExtraction:

    def test_extracts_loan_amount(self, affordability_entities):
        assert affordability_entities.loan_amount == "£307,000"

    def test_extracts_purchase_price(self, affordability_entities):
        assert affordability_entities.purchase_price == "£385,000"

    def test_extracts_ltv_ratio(self, affordability_entities):
        assert affordability_entities.ltv_ratio == "79.7%"

    def test_extracts_stress_test_result(self, affordability_entities):
        assert affordability_entities.stress_test_result == "PASS"

    def test_extracts_property_address(self, affordability_entities):
        assert "Birmingham" in affordability_entities.property_address

    def test_identifies_document_type(self, affordability_entities):
        assert affordability_entities.raw_document_type == "affordability_assessment"


class TestIdVerificationExtraction:

    def test_extracts_applicant_name(self, id_entities):
        assert id_entities.applicant_name == "James Arthur Whitfield"

    def test_extracts_id_verification_status(self, id_entities):
        assert id_entities.id_verification_status == "PASS"

    def test_extracts_date_of_birth(self, id_entities):
        assert id_entities.date_of_birth == "14 March 1988"

    def test_identifies_document_type(self, id_entities):
        assert id_entities.raw_document_type == "id_verification"


class TestCrossDocumentConsistency:

    def test_application_ref_consistent_across_all_documents(
        self, income_entities, affordability_entities, id_entities
    ):
        refs = {
            income_entities.application_reference,
            affordability_entities.application_reference,
            id_entities.application_reference,
        }
        assert len(refs) == 1

    def test_applicant_name_consistent_across_documents(
        self, income_entities, id_entities
    ):
        assert income_entities.applicant_name == id_entities.applicant_name

    def test_dob_consistent_across_documents(
        self, income_entities, id_entities
    ):
        assert income_entities.date_of_birth == id_entities.date_of_birth