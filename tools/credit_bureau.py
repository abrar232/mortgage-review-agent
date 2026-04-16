import logging
import random
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CreditBureauReport:
    applicant_name: str
    date_of_birth: str
    credit_score: int
    score_band: str           # EXCELLENT, GOOD, FAIR, POOR
    active_accounts: int
    total_debt: str
    missed_payments_24m: int
    ccjs: int
    bankruptcies: int
    adverse_credit: bool
    bureau: str               # Experian, Equifax, TransUnion
    recommendation: str       # APPROVE, REFER, DECLINE


def _score_to_band(score: int, bureau: str) -> str:
    if bureau == "Experian":
        if score >= 880:  return "EXCELLENT"
        if score >= 720:  return "GOOD"
        if score >= 560:  return "FAIR"
        return "POOR"
    elif bureau == "Equifax":
        if score >= 604:  return "EXCELLENT"
        if score >= 466:  return "GOOD"
        if score >= 380:  return "FAIR"
        return "POOR"
    else:  # TransUnion
        if score >= 628:  return "EXCELLENT"
        if score >= 604:  return "GOOD"
        if score >= 566:  return "FAIR"
        return "POOR"


def _score_to_recommendation(score: int, bureau: str, missed_payments: int, ccjs: int, bankruptcies: int) -> str:
    # Automatic decline triggers
    if bankruptcies > 0:
        return "DECLINE"
    if ccjs > 2:
        return "DECLINE"

    # Check minimum thresholds per POL-004
    minimums = {"Experian": 700, "Equifax": 420, "TransUnion": 625}
    minimum = minimums.get(bureau, 700)

    if score < minimum * 0.8:
        return "DECLINE"
    if score < minimum:
        return "REFER"
    if missed_payments > 2:
        return "REFER"
    if ccjs > 0:
        return "REFER"

    return "APPROVE"


def get_credit_report(
    applicant_name: str,
    date_of_birth: str,
    bureau: str = "Experian",
    seed: int = None,
) -> CreditBureauReport:
    """
    Mock credit bureau API call.
    Uses applicant name as a seed for deterministic results in testing.
    In production this would be an HTTP call to Experian/Equifax/TransUnion.
    """
    if seed is None:
        seed = sum(ord(c) for c in applicant_name)
    rng = random.Random(seed)

    # Generate realistic credit profile for James Whitfield
    # (deterministic based on name seed)
    if bureau == "Experian":
        score = rng.randint(720, 850)
        max_score = 999
    elif bureau == "Equifax":
        score = rng.randint(430, 580)
        max_score = 700
    else:  # TransUnion
        score = rng.randint(630, 680)
        max_score = 710

    missed_payments = rng.randint(0, 1)
    ccjs = 0
    bankruptcies = 0
    active_accounts = rng.randint(3, 7)
    total_debt = f"£{rng.randint(5000, 25000):,}"

    band = _score_to_band(score, bureau)
    recommendation = _score_to_recommendation(score, bureau, missed_payments, ccjs, bankruptcies)

    logger.info(
        f"Credit bureau check [{bureau}]: {applicant_name} | "
        f"score={score}/{max_score} | band={band} | recommendation={recommendation}"
    )

    return CreditBureauReport(
        applicant_name=applicant_name,
        date_of_birth=date_of_birth,
        credit_score=score,
        score_band=band,
        active_accounts=active_accounts,
        total_debt=total_debt,
        missed_payments_24m=missed_payments,
        ccjs=ccjs,
        bankruptcies=bankruptcies,
        adverse_credit=(missed_payments > 0 or ccjs > 0 or bankruptcies > 0),
        bureau=bureau,
        recommendation=recommendation,
    )


def run_full_credit_check(applicant_name: str, date_of_birth: str) -> dict:
    """Run checks across all three bureaus and return combined result."""
    bureaus = ["Experian", "Equifax", "TransUnion"]
    reports = []

    for bureau in bureaus:
        report = get_credit_report(applicant_name, date_of_birth, bureau)
        reports.append(report)

    recommendations = [r.recommendation for r in reports]

    if "DECLINE" in recommendations:
        overall = "DECLINE"
    elif recommendations.count("REFER") >= 2:
        overall = "REFER"
    elif "REFER" in recommendations:
        overall = "REFER"
    else:
        overall = "APPROVE"

    return {
        "overall_recommendation": overall,
        "reports": [vars(r) for r in reports],
        "adverse_credit_found": any(r.adverse_credit for r in reports),
    }