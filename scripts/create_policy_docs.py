"""
Creates fictional UK mortgage policy documents for the RAG pipeline.
Run once to generate the policy store.
"""

from pathlib import Path

policy_docs = [
    {
        "id": "POL-001-v2.3",
        "title": "Income Verification Policy",
        "content": """
Policy ID: POL-001-v2.3
Title: Income Verification Requirements
Effective Date: 1 January 2024
Approved By: Credit Risk Committee

1. SCOPE
This policy applies to all residential mortgage applications submitted to Northgate Building Society.

2. INCOME DOCUMENTATION REQUIREMENTS
2.1 Employed Applicants
- Minimum 3 months consecutive payslips required
- Most recent P60 or employer reference letter
- Bank statements showing salary credits for last 3 months
- Employment contract for applicants with less than 12 months tenure

2.2 Acceptable Income Types
- Basic salary: 100% of gross annual salary accepted
- Regular overtime: up to 50% of average overtime over 24 months
- Bonuses: up to 50% of average bonus over 24 months if evidenced
- Commission: up to 50% of average commission over 24 months

2.3 Minimum Income Thresholds
- Single applicant: minimum £25,000 gross annual income
- Joint applicants: minimum £35,000 combined gross annual income

3. INCOME MULTIPLE LIMITS
- Maximum loan-to-income ratio: 4.5x gross annual income for standard applications
- Up to 5.5x income permitted for applicants earning above £75,000 subject to enhanced affordability assessment
- Income multiples are calculated on basic salary only; bonus and overtime excluded from multiple calculation

4. VERIFICATION STANDARDS
- All income documents must be dated within 90 days of application
- Documents must be original or certified copies
- Employer details must match Companies House records
"""
    },
    {
        "id": "POL-002-v1.8",
        "title": "Affordability Assessment Policy",
        "content": """
Policy ID: POL-002-v1.8
Title: Affordability Assessment and Stress Testing Requirements
Effective Date: 1 March 2024
Approved By: Credit Risk Committee

1. SCOPE
This policy defines affordability assessment requirements in line with FCA MCOB 11.6 guidelines.

2. AFFORDABILITY CALCULATION
2.1 Committed Expenditure
The following must be included in affordability calculations:
- All existing credit commitments (loans, credit cards, hire purchase)
- Student loan repayments
- Child maintenance payments
- Ground rent and service charges for leasehold properties
- Any other regular financial commitments

2.2 Residual Income Requirements
After mortgage payment and all committed expenditure, minimum residual income:
- Single applicant: £500 per month
- Joint applicants: £750 per month
- Per dependent child: additional £200 per month

3. STRESS TESTING
3.1 Interest Rate Stress Test
- All applications must be stress tested at the higher of:
  a) Initial mortgage rate plus 3%
  b) 8% flat rate
- Application must pass stress test to proceed

3.2 Stress Test Pass Criteria
- Monthly payment at stress rate must not exceed 45% of net monthly income
- Residual income after stress test payment must meet minimum thresholds in section 2.2

4. LOAN-TO-VALUE LIMITS
- Maximum LTV for residential purchase: 90%
- Maximum LTV for remortgage: 85%
- LTV above 85% requires enhanced credit scoring

5. AFFORDABILITY OVERRIDE
- Cases failing affordability by less than 5% may be referred to senior underwriter
- Override must be documented with clear justification
- Maximum 10% of monthly approvals may use affordability override
"""
    },
    {
        "id": "POL-003-v3.1",
        "title": "Identity Verification and AML Policy",
        "content": """
Policy ID: POL-003-v3.1
Title: Identity Verification and Anti-Money Laundering Requirements
Effective Date: 1 January 2024
Approved By: Compliance Committee

1. SCOPE
This policy applies to all mortgage applicants in compliance with the Money Laundering Regulations 2017.

2. IDENTITY VERIFICATION REQUIREMENTS
2.1 Primary ID Documents (one required)
- Valid UK or EU passport
- Valid UK photocard driving licence
- Valid national identity card (EU/EEA nationals)

2.2 Secondary ID Documents (one required)
- Bank or building society statement (dated within 3 months)
- Utility bill (dated within 3 months, not mobile phone)
- Council tax bill (current year)
- HMRC correspondence (dated within 12 months)

2.3 Address Verification
- Current address must be verified with one document from section 2.2
- Applicants at current address less than 3 years must provide previous address verification

3. AML CHECKS
3.1 Mandatory Checks
All applicants must be screened against:
- HM Treasury Sanctions List
- OFAC Sanctions List
- PEP (Politically Exposed Persons) database
- UK fraud prevention databases (CIFAS, National Hunter)

3.2 Enhanced Due Diligence
Enhanced due diligence required for:
- PEP applicants or close associates of PEPs
- Applicants with addresses in high-risk jurisdictions
- Cash deposits forming part of purchase funds exceeding £10,000
- Source of funds cannot be verified through standard means

4. DOCUMENT AUTHENTICITY
- All identity documents must be verified using electronic verification service
- Physical documents inspected for signs of tampering or forgery
- Discrepancies between documents must be investigated before proceeding

5. COMPLIANCE ESCALATION
- Any AML concerns must be reported to the Money Laundering Reporting Officer (MLRO)
- Applications with unresolved AML flags must not proceed without MLRO sign-off
- Suspicious Activity Reports (SARs) filed within 24 hours of identification
"""
    },
    {
        "id": "POL-004-v2.0",
        "title": "Credit Scoring and Bureau Policy",
        "content": """
Policy ID: POL-004-v2.0
Title: Credit Scoring and Credit Bureau Assessment Policy
Effective Date: 1 June 2024
Approved By: Credit Risk Committee

1. SCOPE
This policy defines credit assessment requirements for all residential mortgage applications.

2. CREDIT BUREAU REQUIREMENTS
2.1 Bureau Searches
- Full credit search required with minimum two credit reference agencies
- Approved agencies: Experian, Equifax, TransUnion
- Search must be conducted within 30 days of application submission

2.2 Minimum Credit Score Thresholds
- Experian: minimum score of 700 (out of 999)
- Equifax: minimum score of 420 (out of 700)
- TransUnion: minimum score of 625 (out of 710)
- If scores differ, the middle score is used for assessment

3. ADVERSE CREDIT CRITERIA
3.1 Automatic Decline Triggers
- Bankruptcy or IVA within last 6 years
- Repossession within last 6 years
- CCJ or default over £500 registered in last 3 years
- More than 2 missed mortgage payments in last 24 months

3.2 Referral Triggers (manual review required)
- CCJ or default under £500 registered in last 3 years (if satisfied)
- 1-2 missed mortgage payments in last 24 months
- Debt management plan completed within last 3 years
- Credit score below minimum threshold but above 80% of threshold

4. EXISTING COMMITMENTS
- All existing credit commitments must be declared
- Undisclosed credit commitments identified on bureau search result in automatic referral
- Credit utilisation above 80% on revolving credit requires explanation

5. CREDIT SCORE ENHANCEMENT
- Score below threshold but application otherwise strong may be referred to senior underwriter
- Enhanced scoring criteria apply for applicants with thin credit files (fewer than 3 active accounts)
"""
    },
    {
        "id": "POL-005-v1.2",
        "title": "Human Escalation and Review Policy",
        "content": """
Policy ID: POL-005-v1.2
Title: Human Escalation, Review and Handoff Policy
Effective Date: 1 January 2024
Approved By: Operations Committee

1. SCOPE
This policy defines when automated mortgage review must be escalated to a human underwriter.

2. MANDATORY ESCALATION TRIGGERS
The following conditions require immediate escalation to a human reviewer:
- Any AML or sanctions flag identified during screening
- Applicant identified as PEP or close associate of PEP
- Identity verification failure or document authenticity concern
- Loan amount exceeding £750,000
- LTV exceeding 85%
- Self-employed applicants (require specialist underwriting)
- Applicants with more than 4 existing credit commitments
- Income from multiple sources requiring complex assessment
- Non-standard property types (ex-local authority, high-rise above 6 floors, etc.)
- Any application where automated confidence score is below 75%

3. ESCALATION PROCEDURE
3.1 Handoff Requirements
When escalating to human review, the following must be included:
- Full application reference and applicant details
- Reason for escalation with specific policy clause reference
- All extracted document data and verification results
- Credit bureau results and score
- Automated assessment summary
- Recommended action if applicable

3.2 SLA Requirements
- Standard escalation: reviewed within 2 business days
- Urgent escalation (AML/fraud concern): reviewed within 4 hours
- Complex cases: reviewed within 5 business days

4. AUTOMATED APPROVAL CRITERIA
Applications may proceed without human review only if ALL of the following are met:
- Identity verification: PASS
- AML and sanctions check: CLEAR
- Credit score: above minimum threshold for all bureaus
- Affordability: PASS including stress test
- LTV: 80% or below
- Loan amount: £750,000 or below
- Income type: employed only (PAYE)
- Automated confidence score: 75% or above
- No adverse credit triggers in section 3 of POL-004

5. AUDIT AND OVERSIGHT
- All automated decisions logged with full reasoning trail
- 10% of automated approvals subject to monthly retrospective review
- Any pattern of incorrect automated decisions triggers policy review
"""
    }
]


def create_policy_store():
    output_dir = Path("policy_store")
    output_dir.mkdir(exist_ok=True)

    for doc in policy_docs:
        path = output_dir / f"{doc['id']}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc["content"].strip())
        print(f"Created: {path}")

    print(f"\nCreated {len(policy_docs)} policy documents in policy_store/")


if __name__ == "__main__":
    create_policy_store()