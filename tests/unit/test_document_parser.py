"""
Unit tests for the document parser module.
"""

import pytest
from ingestion.document_parser import parse_document, ParsedDocument


@pytest.fixture
def income_statement():
    return parse_document("samples/income_statement.docx")


@pytest.fixture
def affordability_assessment():
    return parse_document("samples/affordability_assessment.docx")


@pytest.fixture
def id_verification():
    return parse_document("samples/id_verification.docx")


class TestParsedDocumentStructure:

    def test_returns_parsed_document_instance(self, income_statement):
        assert isinstance(income_statement, ParsedDocument)

    def test_has_file_name(self, income_statement):
        assert income_statement.file_name == "income_statement.docx"

    def test_has_file_type(self, income_statement):
        assert income_statement.file_type == "docx"

    def test_has_raw_text(self, income_statement):
        assert isinstance(income_statement.raw_text, str)

    def test_has_page_count(self, income_statement):
        assert isinstance(income_statement.page_count, int)

    def test_page_count_is_positive(self, income_statement):
        assert income_statement.page_count > 0

    def test_raw_text_is_non_empty(self, income_statement):
        assert len(income_statement.raw_text) > 0


class TestIncomeStatement:

    def test_contains_applicant_name(self, income_statement):
        assert "James Arthur Whitfield" in income_statement.raw_text

    def test_contains_employer(self, income_statement):
        assert "Hartwell" in income_statement.raw_text

    def test_contains_salary(self, income_statement):
        assert "72,700" in income_statement.raw_text

    def test_contains_application_ref(self, income_statement):
        assert "MRA-2024-00847" in income_statement.raw_text


class TestAffordabilityAssessment:

    def test_contains_loan_amount(self, affordability_assessment):
        assert "307,000" in affordability_assessment.raw_text

    def test_contains_ltv(self, affordability_assessment):
        assert "79.7%" in affordability_assessment.raw_text

    def test_contains_property_address(self, affordability_assessment):
        assert "Birmingham" in affordability_assessment.raw_text

    def test_contains_stress_test(self, affordability_assessment):
        assert "PASS" in affordability_assessment.raw_text


class TestIdVerification:

    def test_contains_applicant_name(self, id_verification):
        assert "James Arthur Whitfield" in id_verification.raw_text

    def test_contains_verification_status(self, id_verification):
        assert "PASS" in id_verification.raw_text

    def test_contains_passport(self, id_verification):
        assert "Passport" in id_verification.raw_text


class TestUnsupportedFileTypes:

    @pytest.mark.parametrize("filename", [
        "document.csv",
        "document.txt",
        "document.xlsx",
        "document.json",
        "document.png",
    ])
    def test_unsupported_types_raise_value_error(self, filename):
        with pytest.raises(ValueError, match="Unsupported file type"):
            parse_document(filename)