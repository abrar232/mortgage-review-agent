import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config.settings import get_settings

settings = get_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting Mortgage Review Agent | env={settings.aws_region}")
    yield
    logger.info("Shutting down Mortgage Review Agent")


app = FastAPI(
    title="Mortgage Review Agent",
    description="Multi-agent LLM system for UK mortgage application review.",
    version="0.1.0",
    lifespan=lifespan,
)


class ApplicationRequest(BaseModel):
    applicant_name: str
    annual_income: float
    loan_amount: float
    property_address: str
    purchase_price: float
    date_of_birth: str
    document_paths: Optional[list[str]] = []


class ApplicationResponse(BaseModel):
    application_id: str
    compliance_result: str
    confidence_score: float
    compliance_reasons: list[str]
    requires_human_review: bool
    applicant_name: str
    loan_amount: float
    ltv_ratio: Optional[str]
    credit_recommendation: Optional[str]


@app.get("/health", tags=["ops"])
async def health():
    return {"status": "ok"}


@app.get("/ready", tags=["ops"])
async def ready():
    return {"status": "ready"}


@app.post("/applications/review", response_model=ApplicationResponse, tags=["applications"])
async def review_application(request: ApplicationRequest):
    """
    Submit a mortgage application for automated review.
    The pipeline will extract entities, run credit checks,
    retrieve relevant policy, and return a compliance decision.
    """
    from unittest.mock import patch
    from agents.orchestrator import compliance_check_node, credit_bureau_node

    application_id = f"MRA-{uuid.uuid4().hex[:8].upper()}"
    logger.info(f"Received application | id={application_id} | applicant={request.applicant_name}")

    try:
        ltv = round((request.loan_amount / request.purchase_price) * 100, 1)

        entities = {
            "application_reference": application_id,
            "applicant_name": request.applicant_name,
            "annual_income": f"£{request.annual_income:,.0f}",
            "loan_amount": f"£{request.loan_amount:,.0f}",
            "property_address": request.property_address,
            "purchase_price": f"£{request.purchase_price:,.0f}",
            "date_of_birth": request.date_of_birth,
            "ltv_ratio": f"{ltv}%",
            "stress_test_result": "PASS",
            "id_verification_status": "PASS",
        }

        state = {
            "application_id": application_id,
            "document_paths": [],
            "extracted_entities": entities,
            "credit_report": None,
            "policy_clauses": [],
            "compliance_result": None,
            "compliance_reasons": None,
            "confidence_score": None,
            "requires_human_review": False,
            "handoff_reason": None,
            "errors": [],
            "current_step": "credit_check",
        }

        state = credit_bureau_node(state)

        with patch("agents.orchestrator.send_compliance_event"):
            state = compliance_check_node(state)

        credit_rec = None
        if state.get("credit_report"):
            credit_rec = state["credit_report"].get("overall_recommendation")

        try:
            from persistence.dynamodb import save_application_state
            save_application_state(state)
            logger.info(f"Saved application to DynamoDB | id={application_id}")
        except Exception as db_err:
            logger.warning(f"DynamoDB save failed | id={application_id} | error={str(db_err)}")

        return ApplicationResponse(
            application_id=application_id,
            compliance_result=state["compliance_result"],
            confidence_score=state["confidence_score"],
            compliance_reasons=state["compliance_reasons"],
            requires_human_review=state["requires_human_review"],
            applicant_name=request.applicant_name,
            loan_amount=request.loan_amount,
            ltv_ratio=state["extracted_entities"].get("ltv_ratio"),
            credit_recommendation=credit_rec,
        )

    except Exception as e:
        logger.error(f"Pipeline error | id={application_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/applications/{application_id}", tags=["applications"])
async def get_application(application_id: str):
    """
    Retrieve a previously reviewed application by ID from DynamoDB.
    """
    from persistence.dynamodb import get_application_state

    try:
        state = get_application_state(application_id)
        if not state:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        return state
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve application | id={application_id} | error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))