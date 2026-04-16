import logging
from opensearchpy import OpenSearch

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_opensearch_client() -> OpenSearch:
    return OpenSearch(
        hosts=[settings.opensearch_endpoint],
        http_auth=(settings.opensearch_username, settings.opensearch_password),
        use_ssl=True,
        verify_certs=False,
        ssl_show_warn=False,
    )


def retrieve_policy_clauses(query: str, top_k: int = None) -> list[dict]:
    """
    Search OpenSearch for policy clauses relevant to the query.
    Uses BM25 full-text search (OpenSearch default).
    Returns a list of matching chunks with their policy ID and content.
    """
    if top_k is None:
        top_k = settings.rag_top_k

    client = get_opensearch_client()

    search_body = {
        "size": top_k,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["content", "title"],
                "type": "best_fields",
            }
        },
        "_source": ["policy_id", "title", "content", "chunk_id"],
    }

    response = client.search(
        index=settings.opensearch_index_name,
        body=search_body,
    )

    results = []
    for hit in response["hits"]["hits"]:
        results.append({
            "policy_id": hit["_source"]["policy_id"],
            "title": hit["_source"]["title"],
            "content": hit["_source"]["content"],
            "chunk_id": hit["_source"]["chunk_id"],
            "score": hit["_score"],
        })

    logger.info(f"Retrieved {len(results)} policy clauses for query: '{query}'")
    return results