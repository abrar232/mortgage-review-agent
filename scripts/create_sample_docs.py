"""
Generates realistic fictional UK mortgage application documents for testing.
Run once to create sample documents in the samples/ folder.
"""

from pathlib import Path
from docx import Document

output_dir = Path("samples")
output_dir.mkdir(exist_ok=True)


def create_income_statement():
    doc = Document()
    doc.add_heading("Income & Employment Statement", 0)

    doc.add_heading("Applicant Details", level=1)
    doc.add_paragraph("Full Name: James Arthur Whitfield")
    doc.add_paragraph("Date of Birth: 14 March 1988")
    doc.add_paragraph("National Insurance Number: AB123456C")
    doc.add_paragraph("Application Reference: MRA-2024-00847")

    doc.add_heading("Employment Details", level=1)
    doc.add_paragraph("Employer: Hartwell & Sons Engineering Ltd")
    doc.add_paragraph("Employment Type: Permanent, Full-Time")
    doc.add_paragraph("Job Title: Senior Mechanical Engineer")
    doc.add_paragraph("Employment Start Date: 02 September 2017")
    doc.add_paragraph("Employer Address: 14 Industrial Park, Coventry, CV1 2AB")

    doc.add_heading("Income Summary", level=1)
    doc.add_paragraph("Annual Basic Salary: £68,500")
    doc.add_paragraph("Annual Bonus (average last 3 years): £4,200")
    doc.add_paragraph("Total Annual Income: £72,700")
    doc.add_paragraph("Monthly Net Pay (after tax): £4,380")

    doc.add_heading("Payslip History (Last 3 Months)", level=1)
    doc.add_paragraph("October 2024 — Gross: £5,708.33 | Net: £4,380.00")
    doc.add_paragraph("September 2024 — Gross: £5,708.33 | Net: £4,380.00")
    doc.add_paragraph("August 2024 — Gross: £5,708.33 | Net: £4,323.00")

    doc.add_heading("Declaration", level=1)
    doc.add_paragraph(
        "I confirm the above information is accurate and complete to the best of my knowledge. "
        "This statement has been prepared for the purposes of a residential mortgage application "
        "with Northgate Building Society."
    )

    path = output_dir / "income_statement.docx"
    doc.save(path)
    print(f"Created: {path}")


def create_affordability_assessment():
    doc = Document()
    doc.add_heading("Affordability Assessment Report", 0)

    doc.add_heading("Application Details", level=1)
    doc.add_paragraph("Application Reference: MRA-2024-00847")
    doc.add_paragraph("Applicant: James Arthur Whitfield")
    doc.add_paragraph("Property Address: 42 Elmwood Drive, Birmingham, B15 3TN")
    doc.add_paragraph("Purchase Price: £385,000")
    doc.add_paragraph("Requested Loan Amount: £307,000")
    doc.add_paragraph("Loan-to-Value (LTV): 79.7%")
    doc.add_paragraph("Mortgage Term: 25 years")
    doc.add_paragraph("Repayment Type: Capital and Interest")

    doc.add_heading("Monthly Income", level=1)
    doc.add_paragraph("Net Monthly Salary: £4,380.00")
    doc.add_paragraph("Average Monthly Bonus: £350.00")
    doc.add_paragraph("Total Monthly Income: £4,730.00")

    doc.add_heading("Monthly Committed Expenditure", level=1)
    doc.add_paragraph("Existing Loan Repayment (car finance): £320.00")
    doc.add_paragraph("Credit Card Minimum Payment: £85.00")
    doc.add_paragraph("Student Loan Repayment: £210.00")
    doc.add_paragraph("Estimated Living Costs: £950.00")
    doc.add_paragraph("Childcare Costs: £0.00")
    doc.add_paragraph("Total Committed Expenditure: £1,565.00")

    doc.add_heading("Mortgage Payment Assessment", level=1)
    doc.add_paragraph("Monthly Mortgage Payment (at 4.89% initial rate): £1,742.00")
    doc.add_paragraph("Total Monthly Outgoings (incl. mortgage): £3,307.00")
    doc.add_paragraph("Residual Income After All Commitments: £1,423.00")

    doc.add_heading("Stress Test", level=1)
    doc.add_paragraph("Stress Test Rate Applied: 8.00%")
    doc.add_paragraph("Monthly Payment at Stress Rate: £2,361.00")
    doc.add_paragraph("Total Outgoings at Stress Rate: £3,926.00")
    doc.add_paragraph("Residual Income at Stress Rate: £804.00")
    doc.add_paragraph("Stress Test Result: PASS — residual income exceeds minimum threshold of £500.00")

    doc.add_heading("Affordability Conclusion", level=1)
    doc.add_paragraph(
        "Based on the information provided, the applicant demonstrates sufficient affordability "
        "for the requested mortgage. The application meets Northgate Building Society's minimum "
        "income multiple of 4.5x and passes the FCA-mandated stress test at 8.00%. "
        "This assessment is subject to satisfactory credit bureau checks and policy compliance review."
    )

    path = output_dir / "affordability_assessment.docx"
    doc.save(path)
    print(f"Created: {path}")


def create_id_verification():
    doc = Document()
    doc.add_heading("Identity Verification Document", 0)

    doc.add_heading("Applicant Details", level=1)
    doc.add_paragraph("Full Name: James Arthur Whitfield")
    doc.add_paragraph("Date of Birth: 14 March 1988")
    doc.add_paragraph("Nationality: British")
    doc.add_paragraph("Application Reference: MRA-2024-00847")

    doc.add_heading("Primary ID — Passport", level=1)
    doc.add_paragraph("Document Type: UK Passport")
    doc.add_paragraph("Passport Number: 536274819")
    doc.add_paragraph("Issue Date: 22 July 2019")
    doc.add_paragraph("Expiry Date: 22 July 2029")
    doc.add_paragraph("Issuing Authority: His Majesty's Passport Office")
    doc.add_paragraph("Verification Status: VERIFIED")

    doc.add_heading("Secondary ID — Driving Licence", level=1)
    doc.add_paragraph("Document Type: UK Full Driving Licence")
    doc.add_paragraph("Licence Number: WHITF881143JA9AB")
    doc.add_paragraph("Issue Date: 05 March 2009")
    doc.add_paragraph("Expiry Date: 14 March 2028")
    doc.add_paragraph("Issuing Authority: DVLA")
    doc.add_paragraph("Verification Status: VERIFIED")

    doc.add_heading("Address Verification", level=1)
    doc.add_paragraph("Current Address: 18 Birchfield Road, Solihull, B91 1QP")
    doc.add_paragraph("Residency at Address: 6 years 4 months")
    doc.add_paragraph("Proof of Address Document: Utility bill (October 2024)")
    doc.add_paragraph("Address Verification Status: CONFIRMED")

    doc.add_heading("AML & Sanctions Check", level=1)
    doc.add_paragraph("PEP (Politically Exposed Person) Check: CLEAR")
    doc.add_paragraph("Sanctions List Check: CLEAR")
    doc.add_paragraph("Fraud Database Check: CLEAR")
    doc.add_paragraph("Overall ID Verification Outcome: PASS")

    path = output_dir / "id_verification.docx"
    doc.save(path)
    print(f"Created: {path}")


if __name__ == "__main__":
    create_income_statement()
    create_affordability_assessment()
    create_id_verification()
    print("\nAll sample documents created in samples/")