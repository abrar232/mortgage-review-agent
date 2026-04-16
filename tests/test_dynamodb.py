import logging
logging.basicConfig(level=logging.INFO)

from persistence.dynamodb import (
    save_application_state,
    get_application_state,
    save_conversation_memory,
    get_conversation_memory,
)

# Test saving state
fake_state = {
    "application_id": "MRA-2024-00847",
    "current_step": "compliance",
    "compliance_result": "PASS",
    "confidence_score": 0.9,
    "requires_human_review": False,
    "handoff_reason": None,
    "extracted_entities": {
        "applicant_name": "James Arthur Whitfield",
        "annual_income": "£72,700",
        "ltv_ratio": "79.7%",
    },
    "compliance_reasons": ["✓ ID verification passed", "✓ Stress test passed"],
    "errors": [],
}

print("Saving application state...")
save_application_state(fake_state)

print("Retrieving application state...")
retrieved = get_application_state("MRA-2024-00847")
print(f"Application ID:    {retrieved['application_id']}")
print(f"Compliance result: {retrieved['compliance_result']}")
print(f"Confidence score:  {retrieved['confidence_score']}")
print(f"Current step:      {retrieved['current_step']}")
print(f"Entities:          {retrieved['extracted_entities']}")

print("\nSaving conversation memory...")
messages = [
    {"role": "user", "content": "Review application MRA-2024-00847"},
    {"role": "assistant", "content": "Parsed 3 documents, compliance PASS"},
]
save_conversation_memory("MRA-2024-00847", messages)

print("Retrieving conversation memory...")
memory = get_conversation_memory("MRA-2024-00847")
for msg in memory:
    print(f"  [{msg['role']}]: {msg['content']}")