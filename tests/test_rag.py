from rag.retriever import retrieve_policy_clauses

queries = [
    "What is the maximum loan to income ratio?",
    "What documents are required for identity verification?",
    "When should an application be escalated to a human reviewer?",
    "What is the stress test rate for affordability?",
]

for query in queries:
    print(f"\n{'='*50}")
    print(f"Query: {query}")
    results = retrieve_policy_clauses(query, top_k=2)
    for r in results:
        print(f"\n  Policy: {r['policy_id']} (score: {r['score']:.2f})")
        print(f"  Preview: {r['content'][:200]}...")