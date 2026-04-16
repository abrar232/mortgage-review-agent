"""
Evaluation: RAG Retrieval Quality
Tests whether the retriever returns the most relevant policy document
for a range of compliance-related queries.
"""

from rag.retriever import retrieve_policy_clauses

# Each test case has a query and the policy ID we expect to appear in top results
TEST_CASES = [
    {
        "query": "What is the maximum loan to income ratio allowed?",
        "expected_policy": "POL-001-v2.3",
        "description": "Income multiple limit",
    },
    {
        "query": "What is the stress test interest rate for affordability?",
        "expected_policy": "POL-002-v1.8",
        "description": "Stress test rate",
    },
    {
        "query": "What documents are required for identity verification?",
        "expected_policy": "POL-003-v3.1",
        "description": "ID verification documents",
    },
    {
        "query": "What is the minimum credit score threshold for Experian?",
        "expected_policy": "POL-004-v2.0",
        "description": "Credit score threshold",
    },
    {
        "query": "When must an application be escalated to a human underwriter?",
        "expected_policy": "POL-005-v1.2",
        "description": "Escalation triggers",
    },
    {
        "query": "What happens if an applicant is a politically exposed person?",
        "expected_policy": "POL-003-v3.1",
        "description": "PEP handling",
    },
    {
        "query": "What is the maximum LTV for automated approval?",
        "expected_policy": "POL-005-v1.2",
        "description": "LTV automated approval limit",
    },
    {
        "query": "What are the automatic decline triggers for adverse credit?",
        "expected_policy": "POL-004-v2.0",
        "description": "Adverse credit decline",
    },
]


def run_rag_eval(top_k: int = 3):
    from evaluations.eval_logger import save_eval_results

    print("=" * 60)
    print("RAG RETRIEVAL EVALUATION")
    print("=" * 60)

    total = len(TEST_CASES)
    passed = 0
    cases = []

    for case in TEST_CASES:
        results = retrieve_policy_clauses(case["query"], top_k=top_k)
        retrieved_ids = [r["policy_id"] for r in results]
        expected = case["expected_policy"]
        correct = expected in retrieved_ids
        rank = retrieved_ids.index(expected) + 1 if correct else None

        if correct:
            passed += 1
            print(f"  ✓ [{case['description']}] — found {expected} at rank {rank}")
        else:
            print(f"  ✗ [{case['description']}]")
            print(f"      Expected: {expected}")
            print(f"      Retrieved: {retrieved_ids}")

        cases.append({
            "query": case["query"],
            "description": case["description"],
            "expected_policy": expected,
            "retrieved_policies": retrieved_ids,
            "rank": rank,
            "passed": correct,
        })

    accuracy = round(passed / total * 100, 1)
    print(f"\n{'=' * 60}")
    print(f"RAG RESULTS: {passed}/{total} queries correct ({accuracy}%)")
    print("=" * 60)

    save_eval_results("rag", {
        "summary": {"passed": passed, "total": total, "accuracy_pct": accuracy},
        "cases": cases,
    })

    return passed, total


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.WARNING)
    run_rag_eval()