import logging
from langgraph.graph import StateGraph, END
from persistence.dynamodb import save_application_state
from state.schema import ApplicationState
from ingestion.document_parser import parse_document
from agents.extraction_agent import extract_entities
from rag.retriever import retrieve_policy_clauses
from tools.credit_bureau import run_full_credit_check
from messaging.sqs import send_compliance_event, send_handoff_event
from monitoring.cloudwatch import track_application_review

logger = logging.getLogger(__name__)


# ── Node 1: Document Parsing & Extraction ─────────────────────────────────────
def parse_documents_node(state: ApplicationState) -> ApplicationState:
    logger.info(f"[{state['application_id']}] Parsing documents...")
    state["current_step"] = "parsing"

    all_entities = {}
    errors = []

    for path in state["document_paths"]:
        try:
            parsed = parse_document(path)
            entities = extract_entities(parsed)
            for field, value in vars(entities).items():
                if value != "NOT_FOUND" or field not in all_entities:
                    all_entities[field] = value
        except Exception as e:
            errors.append(f"Failed to process {path}: {str(e)}")
            logger.error(f"Error processing {path}: {e}")

    state["extracted_entities"] = all_entities
    state["errors"] = errors
    return state


# ── Node 2: Credit Bureau Check ───────────────────────────────────────────────
def credit_bureau_node(state: ApplicationState) -> ApplicationState:
    logger.info(f"[{state['application_id']}] Running credit bureau checks...")
    state["current_step"] = "credit_check"

    entities = state.get("extracted_entities", {})
    applicant_name = entities.get("applicant_name", "NOT_FOUND")
    date_of_birth = entities.get("date_of_birth", "NOT_FOUND")

    if applicant_name == "NOT_FOUND":
        state["errors"] = (state.get("errors") or []) + ["Could not extract applicant name for credit check"]
        state["credit_report"] = None
        return state

    credit_result = run_full_credit_check(applicant_name, date_of_birth)
    state["credit_report"] = credit_result
    return state


# ── Node 3: RAG Policy Retrieval ──────────────────────────────────────────────
def retrieve_policy_node(state: ApplicationState) -> ApplicationState:
    logger.info(f"[{state['application_id']}] Retrieving policy clauses...")
    state["current_step"] = "rag_retrieval"

    entities = state.get("extracted_entities", {})
    query_parts = []

    if entities.get("ltv_ratio") != "NOT_FOUND":
        query_parts.append(f"LTV ratio {entities['ltv_ratio']}")
    if entities.get("stress_test_result") != "NOT_FOUND":
        query_parts.append(f"stress test {entities['stress_test_result']}")
    if entities.get("id_verification_status") != "NOT_FOUND":
        query_parts.append(f"identity verification {entities['id_verification_status']}")

    query_parts.append("mortgage application compliance requirements escalation")
    query = " ".join(query_parts)

    clauses = retrieve_policy_clauses(query, top_k=3)
    state["policy_clauses"] = clauses
    return state


# ── Node 4: Compliance Check ──────────────────────────────────────────────────
def compliance_check_node(state: ApplicationState) -> ApplicationState:
    logger.info(f"[{state['application_id']}] Running compliance check...")
    state["current_step"] = "compliance"

    entities = state.get("extracted_entities", {})
    credit = state.get("credit_report", {})
    reasons = []
    confidence = 1.0

    # Rule 1: ID verification
    if entities.get("id_verification_status") == "PASS":
        reasons.append("✓ ID verification passed")
    elif entities.get("id_verification_status") == "NOT_FOUND":
        reasons.append("⚠ ID verification status not found")
        confidence -= 0.2
    else:
        reasons.append("✗ ID verification failed")
        confidence -= 0.4

    # Rule 2: Stress test
    if entities.get("stress_test_result") == "PASS":
        reasons.append("✓ Affordability stress test passed")
    elif entities.get("stress_test_result") == "NOT_FOUND":
        reasons.append("⚠ Stress test result not found")
        confidence -= 0.2
    else:
        reasons.append("✗ Affordability stress test failed")
        confidence -= 0.4

    # Rule 3: LTV check
    ltv = entities.get("ltv_ratio", "NOT_FOUND")
    if ltv != "NOT_FOUND":
        try:
            ltv_value = float(ltv.replace("%", "").strip())
            if ltv_value <= 80:
                reasons.append(f"✓ LTV {ltv} within automated approval limit (≤80%)")
            elif ltv_value <= 85:
                reasons.append(f"⚠ LTV {ltv} requires enhanced credit scoring (>80%)")
                confidence -= 0.1
            else:
                reasons.append(f"✗ LTV {ltv} exceeds maximum for automated approval (>85%)")
                confidence -= 0.3
        except ValueError:
            reasons.append(f"⚠ Could not parse LTV value: {ltv}")
            confidence -= 0.1
    else:
        reasons.append("⚠ LTV ratio not found")
        confidence -= 0.15

    # Rule 4: Credit bureau result
    if credit:
        overall = credit.get("overall_recommendation", "NOT_FOUND")
        if overall == "APPROVE":
            reasons.append("✓ Credit bureau checks passed (all 3 bureaus)")
        elif overall == "REFER":
            reasons.append("⚠ Credit bureau flagged for manual review")
            confidence -= 0.2
        elif overall == "DECLINE":
            reasons.append("✗ Credit bureau recommends decline")
            confidence -= 0.5

        if credit.get("adverse_credit_found"):
            reasons.append("⚠ Adverse credit history found — referral required per POL-004")
            confidence -= 0.1
    else:
        reasons.append("⚠ Credit bureau check not completed")
        confidence -= 0.25

    # Determine result
    confidence = max(0.0, round(confidence, 2))
    state["confidence_score"] = confidence

    from config.settings import get_settings
    threshold = get_settings().compliance_confidence_threshold

    # Hard fail triggers — regardless of confidence score
    hard_fail = (
        entities.get("id_verification_status") not in ("PASS", "NOT_FOUND") or
        credit and credit.get("overall_recommendation") == "DECLINE"
    )

    if hard_fail:
        state["compliance_result"] = "FAIL"
        state["requires_human_review"] = True
        state["handoff_reason"] = "Hard fail trigger — ID verification failed or credit bureau decline"
    elif confidence >= threshold:
        state["compliance_result"] = "PASS"
        state["requires_human_review"] = False
    elif confidence >= 0.5:
        state["compliance_result"] = "ESCALATE"
        state["requires_human_review"] = True
        state["handoff_reason"] = f"Confidence score {confidence} below automated approval threshold of {threshold}"
    else:
        state["compliance_result"] = "FAIL"
        state["requires_human_review"] = True
        state["handoff_reason"] = f"Multiple compliance failures — confidence score {confidence}"

    state["compliance_reasons"] = reasons

    send_compliance_event(
        application_id=state["application_id"],
        compliance_result=state["compliance_result"],
        confidence=state["confidence_score"],
    )
    return state


# ── Node 5: Human Handoff ─────────────────────────────────────────────────────
def human_handoff_node(state: ApplicationState) -> ApplicationState:
    logger.info(f"[{state['application_id']}] Escalating to human reviewer...")
    state["current_step"] = "human_handoff"

    print(f"\n🚨 ESCALATION: Application {state['application_id']}")
    print(f"   Reason: {state.get('handoff_reason')}")
    print(f"   Confidence score: {state.get('confidence_score')}")
    print(f"   Compliance result: {state.get('compliance_result')}")
    print(f"   Application queued for human review.")

    send_handoff_event(
        application_id=state["application_id"],
        reason=state.get("handoff_reason", ""),
        confidence=state.get("confidence_score", 0.0),
    )
    return state


# ── Routing logic ─────────────────────────────────────────────────────────────
def route_after_compliance(state: ApplicationState) -> str:
    if state.get("requires_human_review"):
        return "human_handoff"
    return END


# ── Build the graph ───────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(ApplicationState)

    graph.add_node("parse_documents", parse_documents_node)
    graph.add_node("credit_check", credit_bureau_node)
    graph.add_node("retrieve_policy", retrieve_policy_node)
    graph.add_node("compliance_check", compliance_check_node)
    graph.add_node("human_handoff", human_handoff_node)

    graph.set_entry_point("parse_documents")
    graph.add_edge("parse_documents", "credit_check")
    graph.add_edge("credit_check", "retrieve_policy")
    graph.add_edge("retrieve_policy", "compliance_check")
    graph.add_conditional_edges(
        "compliance_check",
        route_after_compliance,
        {
            "human_handoff": "human_handoff",
            END: END,
        }
    )
    graph.add_edge("human_handoff", END)

    return graph.compile()


def run_application_review(application_id: str, document_paths: list[str]) -> dict:
    import time

    graph = build_graph()

    initial_state: ApplicationState = {
        "application_id": application_id,
        "document_paths": document_paths,
        "extracted_entities": None,
        "policy_clauses": None,
        "credit_report": None,
        "compliance_result": None,
        "compliance_reasons": None,
        "confidence_score": None,
        "requires_human_review": False,
        "handoff_reason": None,
        "errors": None,
        "current_step": None,
    }

    start = time.time()
    final_state = graph.invoke(initial_state)
    duration = round(time.time() - start, 2)

    track_application_review(
        application_id=application_id,
        compliance_result=final_state.get("compliance_result", "UNKNOWN"),
        confidence=final_state.get("confidence_score", 0.0),
        duration_seconds=duration,
    )

    save_application_state(final_state)
    return final_state