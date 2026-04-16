from tools.credit_bureau import run_full_credit_check

result = run_full_credit_check(
    applicant_name="James Arthur Whitfield",
    date_of_birth="14 March 1988",
)

print(f"Overall recommendation: {result['overall_recommendation']}")
print(f"Adverse credit found:   {result['adverse_credit_found']}")
print()

for report in result["reports"]:
    print(f"Bureau:          {report['bureau']}")
    print(f"Score:           {report['credit_score']} ({report['score_band']})")
    print(f"Active accounts: {report['active_accounts']}")
    print(f"Total debt:      {report['total_debt']}")
    print(f"Missed payments: {report['missed_payments_24m']} (last 24 months)")
    print(f"CCJs:            {report['ccjs']}")
    print(f"Recommendation:  {report['recommendation']}")
    print()