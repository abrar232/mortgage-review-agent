from typing import TypedDict, Optional


class ApplicationState(TypedDict):
    # ── Input ─────────────────────────────────────────────────────────────────
    application_id: str
    document_paths: list[str]

    # ── Extraction results ────────────────────────────────────────────────────
    extracted_entities: Optional[dict]

    # ── Credit bureau ─────────────────────────────────────────────────────────
    credit_report: Optional[dict]

    # ── RAG results ───────────────────────────────────────────────────────────
    policy_clauses: Optional[list[dict]]

    # ── Compliance results ────────────────────────────────────────────────────
    compliance_result: Optional[str]
    compliance_reasons: Optional[list[str]]
    confidence_score: Optional[float]

    # ── Handoff ───────────────────────────────────────────────────────────────
    requires_human_review: bool
    handoff_reason: Optional[str]

    # ── Metadata ──────────────────────────────────────────────────────────────
    errors: Optional[list[str]]
    current_step: Optional[str]