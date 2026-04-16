import logging
logging.basicConfig(level=logging.INFO)

from agents.orchestrator import run_application_review

result = run_application_review(
    application_id="MRA-2024-00847",
    document_paths=[
        "samples/income_statement.docx",
        "samples/affordability_assessment.docx",
        "samples/id_verification.docx",
    ]
)

print("\n" + "="*50)
print("FINAL REVIEW RESULT")
print("="*50)
print(f"Application ID:   {result['application_id']}")
print(f"Compliance:       {result['compliance_result']}")
print(f"Confidence:       {result['confidence_score']}")
print(f"Human review:     {result['requires_human_review']}")
print(f"\nReasons:")
for r in result.get("compliance_reasons", []):
    print(f"  {r}")
if result.get("errors"):
    print(f"\nErrors:")
    for e in result["errors"]:
        print(f"  {e}")