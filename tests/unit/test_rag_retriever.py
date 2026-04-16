"""
Unit tests for the RAG retriever module.
"""

import pytest
from rag.retriever import retrieve_policy_clauses


EXPECTED_FIELDS = {"policy_id", "title", "content", "chunk_id", "score"}


@pytest.fixture
def single_result():
    return retrieve_policy_clauses("mortgage policy compliance", top_k=1)


@pytest.fixture
def multiple_results():
    return retrieve_policy_clauses("mortgage policy compliance", top_k=3)


class TestRetrieverOutput:

    def test_returns_list(self, single_result):
        assert isinstance(single_result, list)

    def test_returns_results(self, multiple_results):
        assert len(multiple_results) > 0

    def test_top_k_one_returns_one_result(self, single_result):
        assert len(single_result) == 1

    def test_top_k_limits_results(self):
        results = retrieve_policy_clauses("mortgage policy", top_k=2)
        assert len(results) <= 2

    def test_result_has_all_required_fields(self, single_result):
        assert EXPECTED_FIELDS.issubset(single_result[0].keys())

    def test_content_is_non_empty(self, multiple_results):
        for r in multiple_results:
            assert len(r["content"]) > 0

    def test_scores_are_positive(self, multiple_results):
        for r in multiple_results:
            assert r["score"] > 0

    def test_policy_ids_are_strings(self, multiple_results):
        for r in multiple_results:
            assert isinstance(r["policy_id"], str)


class TestPolicyRetrieval:

    @pytest.mark.parametrize("query,expected_policy", [
        ("maximum loan to income ratio", "POL-001-v2.3"),
        ("stress test affordability interest rate", "POL-002-v1.8"),
        ("identity verification documents required", "POL-003-v3.1"),
        ("minimum credit score threshold Experian", "POL-004-v2.0"),
        ("when to escalate to human underwriter", "POL-005-v1.2"),
        ("AML sanctions politically exposed person", "POL-003-v3.1"),
        ("LTV automated approval limit", "POL-005-v1.2"),
        ("adverse credit decline CCJ bankruptcy", "POL-004-v2.0"),
    ])
    def test_query_retrieves_correct_policy(self, query, expected_policy):
        results = retrieve_policy_clauses(query, top_k=3)
        policy_ids = [r["policy_id"] for r in results]
        assert expected_policy in policy_ids, (
            f"Expected {expected_policy} in results for query: '{query}'\n"
            f"Got: {policy_ids}"
        )

    def test_income_policy_ranks_first_for_income_query(self):
        results = retrieve_policy_clauses("income verification salary requirements", top_k=3)
        assert results[0]["policy_id"] == "POL-001-v2.3"

    def test_escalation_policy_ranks_first_for_escalation_query(self):
        results = retrieve_policy_clauses("when must application escalate human reviewer", top_k=3)
        assert results[0]["policy_id"] == "POL-005-v1.2"