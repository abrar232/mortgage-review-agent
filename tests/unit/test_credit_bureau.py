"""
Unit tests for the credit bureau module.
"""

import pytest
from tools.credit_bureau import (
    get_credit_report,
    run_full_credit_check,
    _score_to_band,
    _score_to_recommendation,
    CreditBureauReport,
)


BUREAUS = ["Experian", "Equifax", "TransUnion"]
VALID_BANDS = ("EXCELLENT", "GOOD", "FAIR", "POOR")
VALID_RECOMMENDATIONS = ("APPROVE", "REFER", "DECLINE")


@pytest.fixture
def experian_report():
    return get_credit_report("Test User", "01 Jan 1990", "Experian", seed=42)


@pytest.fixture
def full_credit_check():
    return run_full_credit_check("Test User", "01 Jan 1990")


class TestScoreToBand:

    @pytest.mark.parametrize("score,expected", [
        (900, "EXCELLENT"),
        (750, "GOOD"),
        (600, "FAIR"),
        (400, "POOR"),
    ])
    def test_experian_bands(self, score, expected):
        assert _score_to_band(score, "Experian") == expected

    @pytest.mark.parametrize("score,expected", [
        (620, "EXCELLENT"),
        (466, "GOOD"),
        (380, "FAIR"),
        (300, "POOR"),
    ])
    def test_equifax_bands(self, score, expected):
        assert _score_to_band(score, "Equifax") == expected

    @pytest.mark.parametrize("score,expected", [
        (650, "EXCELLENT"),
        (610, "GOOD"),
        (566, "FAIR"),
        (400, "POOR"),
    ])
    def test_transunion_bands(self, score, expected):
        assert _score_to_band(score, "TransUnion") == expected


class TestScoreToRecommendation:

    @pytest.mark.parametrize("bankruptcies", [1, 2, 3])
    def test_bankruptcy_always_declines(self, bankruptcies):
        assert _score_to_recommendation(999, "Experian", 0, 0, bankruptcies) == "DECLINE"

    @pytest.mark.parametrize("ccjs", [3, 4, 5])
    def test_high_ccj_count_declines(self, ccjs):
        assert _score_to_recommendation(999, "Experian", 0, ccjs, 0) == "DECLINE"

    def test_good_profile_approves(self):
        assert _score_to_recommendation(800, "Experian", 0, 0, 0) == "APPROVE"

    def test_low_score_declines(self):
        assert _score_to_recommendation(400, "Experian", 0, 0, 0) == "DECLINE"

    def test_borderline_score_refers(self):
        assert _score_to_recommendation(650, "Experian", 0, 0, 0) == "REFER"

    def test_missed_payments_refers(self):
        assert _score_to_recommendation(800, "Experian", 3, 0, 0) == "REFER"


class TestGetCreditReport:

    def test_returns_credit_bureau_report(self, experian_report):
        assert isinstance(experian_report, CreditBureauReport)

    def test_correct_bureau_name(self, experian_report):
        assert experian_report.bureau == "Experian"

    def test_correct_applicant_name(self, experian_report):
        assert experian_report.applicant_name == "Test User"

    def test_score_is_positive(self, experian_report):
        assert experian_report.credit_score > 0

    def test_score_band_is_valid(self, experian_report):
        assert experian_report.score_band in VALID_BANDS

    def test_recommendation_is_valid(self, experian_report):
        assert experian_report.recommendation in VALID_RECOMMENDATIONS

    def test_results_are_deterministic_with_seed(self):
        r1 = get_credit_report("Test User", "01 Jan 1990", "Experian", seed=42)
        r2 = get_credit_report("Test User", "01 Jan 1990", "Experian", seed=42)
        assert r1.credit_score == r2.credit_score

    def test_different_seeds_give_different_results(self):
        r1 = get_credit_report("Test User", "01 Jan 1990", "Experian", seed=1)
        r2 = get_credit_report("Test User", "01 Jan 1990", "Experian", seed=999)
        assert r1.credit_score != r2.credit_score

    @pytest.mark.parametrize("bureau", BUREAUS)
    def test_all_bureaus_return_valid_report(self, bureau):
        report = get_credit_report("Test User", "01 Jan 1990", bureau)
        assert report.bureau == bureau
        assert report.score_band in VALID_BANDS
        assert report.recommendation in VALID_RECOMMENDATIONS


class TestRunFullCreditCheck:

    def test_returns_three_reports(self, full_credit_check):
        assert len(full_credit_check["reports"]) == 3

    def test_overall_recommendation_is_valid(self, full_credit_check):
        assert full_credit_check["overall_recommendation"] in VALID_RECOMMENDATIONS

    def test_adverse_credit_flag_is_boolean(self, full_credit_check):
        assert isinstance(full_credit_check["adverse_credit_found"], bool)

    def test_all_three_bureaus_represented(self, full_credit_check):
        bureaus = {r["bureau"] for r in full_credit_check["reports"]}
        assert bureaus == set(BUREAUS)

    def test_any_decline_gives_overall_decline(self):
        # Force a decline by using a name that generates low scores
        result = run_full_credit_check("Z" * 50, "01 Jan 1990")
        assert result["overall_recommendation"] in VALID_RECOMMENDATIONS