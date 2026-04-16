import logging
from pathlib import Path
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


def create_index(client: OpenSearch) -> None:
    index_name = settings.opensearch_index_name

    if client.indices.exists(index=index_name):
        logger.info(f"Index '{index_name}' already exists, skipping creation.")
        return

    index_body = {
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
            }
        },
        "mappings": {
            "properties": {
                "policy_id": {"type": "keyword"},
                "title":     {"type": "text"},
                "content":   {"type": "text"},
                "chunk_id":  {"type": "keyword"},
            }
        }
    }

    client.indices.create(index=index_name, body=index_body)
    logger.info(f"Created index '{index_name}'")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks for better retrieval."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def index_policy_documents(policy_store_path: str = "policy_store") -> None:
    client = get_opensearch_client()
    create_index(client)

    policy_dir = Path(policy_store_path)
    total_chunks = 0

    for policy_file in sorted(policy_dir.glob("*.txt")):
        policy_id = policy_file.stem
        content = policy_file.read_text(encoding="utf-8")

        # Extract title from first line
        first_line = content.strip().split("\n")[0]
        title = first_line.replace("Policy ID:", "").strip()

        chunks = chunk_text(content)
        logger.info(f"Indexing {policy_file.name}: {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            doc = {
                "policy_id": policy_id,
                "title": title,
                "content": chunk,
                "chunk_id": f"{policy_id}-chunk-{i}",
            }

            client.index(
                index=settings.opensearch_index_name,
                id=f"{policy_id}-chunk-{i}",
                body=doc,
            )
            total_chunks += 1

    logger.info(f"Indexed {total_chunks} chunks from {policy_store_path}")
    print(f"Done — indexed {total_chunks} chunks into '{settings.opensearch_index_name}'")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    index_policy_documents()