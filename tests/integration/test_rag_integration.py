"""
Integration tests: RAG Retrieval in pipeline context
Tests that OpenSearch retrieval works correctly when called
as part of the broader pipeline flow.
"""

import pytest
from rag.retriever import retrieve_policy_clauses
from rag.indexer import get_opensearch_client
from config.settings import get_settings

settings = get_settings()


@pytest.fixture(scope="module")
def opensearch_client():
    return get_opensearch_client()


class TestOpenSearchConnection:

    def test_index_exists(self, opensearch_client):
        try:
            exists = opensearch_client.indices.exists(index=settings.opensearch_index_name)
            assert exists
        except Exception:
            response = opensearch_client.count(index=settings.opensearch_index_name)
            assert response["count"] > 0

    def test_index_has_documents(self, opensearch_client):
        response = opensearch_client.count(index=settings.opensearch_index_name)
        assert response["count"] > 0

    def test_all_five_policies_indexed(self, opensearch_client):
        expected = {
            "POL-001-v2.3",
            "POL-002-v1.8",
            "POL-003-v3.1",
            "POL-004-v2.0",
            "POL-005-v1.2",
        }
        response = opensearch_client.search(
            index=settings.opensearch_index_name,
            body={"size": 10, "query": {"match_all": {}}, "_source": ["policy_id"]},
        )
        indexed_ids = {hit["_source"]["policy_id"] for hit in response["hits"]["hits"]}
        assert expected.issubset(indexed_ids)


class TestRAGInPipelineContext:

    def test_query_built_from_extracted_entities(self):
        entities = {
            "ltv_ratio": "79.7%",
            "stress_test_result": "PASS",
            "id_verification_status": "PASS",
        }
        query_parts = []
        if entities.get("ltv_ratio") != "NOT_FOUND":
            query_parts.append(f"LTV ratio {entities['ltv_ratio']}")
        if entities.get("stress_test_result") != "NOT_FOUND":
            query_parts.append(f"stress test {entities['stress_test_result']}")
        if entities.get("id_verification_status") != "NOT_FOUND":
            query_parts.append(f"identity verification {entities['id_verification_status']}")
        query_parts.append("mortgage application compliance requirements escalation")
        query = " ".join(query_parts)

        results = retrieve_policy_clauses(query, top_k=3)
        assert len(results) == 3

    def test_pipeline_query_retrieves_compliance_policy(self):
        query = "LTV ratio 79.7% stress test PASS identity verification PASS mortgage compliance"
        results = retrieve_policy_clauses(query, top_k=3)
        policy_ids = [r["policy_id"] for r in results]
        assert "POL-005-v1.2" in policy_ids

    def test_high_ltv_query_retrieves_affordability_policy(self):
        query = "LTV ratio 88% exceeds threshold automated approval limit"
        results = retrieve_policy_clauses(query, top_k=3)
        policy_ids = [r["policy_id"] for r in results]
        assert "POL-002-v1.8" in policy_ids or "POL-005-v1.2" in policy_ids

    def test_failed_id_query_retrieves_id_policy(self):
        query = "identity verification FAIL document name mismatch AML check"
        results = retrieve_policy_clauses(query, top_k=3)
        policy_ids = [r["policy_id"] for r in results]
        assert "POL-003-v3.1" in policy_ids

    def test_results_contain_actionable_content(self):
        results = retrieve_policy_clauses("mortgage compliance escalation", top_k=3)
        for result in results:
            assert len(result["content"]) > 50
            assert result["policy_id"].startswith("POL-")


class TestRAGScoring:

    def test_more_specific_query_scores_higher(self):
        specific = retrieve_policy_clauses("minimum Experian credit score 700", top_k=1)
        generic = retrieve_policy_clauses("mortgage", top_k=1)
        assert specific[0]["score"] >= generic[0]["score"]

    def test_exact_policy_term_retrieves_correct_document(self):
        results = retrieve_policy_clauses("Politically Exposed Person PEP enhanced due diligence", top_k=3)
        policy_ids = [r["policy_id"] for r in results]
        assert "POL-003-v3.1" in policy_ids

    @pytest.mark.parametrize("top_k", [1, 2, 3, 5])
    def test_top_k_parameter_respected(self, top_k):
        results = retrieve_policy_clauses("mortgage policy", top_k=top_k)
        assert len(results) <= top_k