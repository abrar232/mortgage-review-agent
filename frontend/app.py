import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Northgate Building Society",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 Northgate Building Society")
st.subheader("Automated Mortgage Application Review")
st.markdown("---")

with st.form("application_form"):
    st.markdown("### Applicant Details")

    col1, col2 = st.columns(2)

    with col1:
        applicant_name = st.text_input("Full Name", placeholder="James Arthur Whitfield")
        date_of_birth = st.text_input("Date of Birth", placeholder="14 March 1988")
        annual_income = st.number_input("Annual Income (£)", min_value=0, value=0, step=1000)

    with col2:
        loan_amount = st.number_input("Loan Amount (£)", min_value=0, value=0, step=1000)
        purchase_price = st.number_input("Purchase Price (£)", min_value=0, value=0, step=1000)
        property_address = st.text_input("Property Address", placeholder="14 Elmsworth Avenue, Birmingham, B15 2TH")

    submitted = st.form_submit_button("🔍 Run Compliance Review", use_container_width=True)

if submitted:
    if not all([applicant_name, date_of_birth, annual_income, loan_amount, purchase_price, property_address]):
        st.error("Please fill in all fields before submitting.")
    else:
        with st.spinner("Running compliance review — this may take a few seconds..."):
            try:
                response = requests.post(
                    f"{API_URL}/applications/review",
                    json={
                        "applicant_name": applicant_name,
                        "date_of_birth": date_of_birth,
                        "annual_income": annual_income,
                        "loan_amount": loan_amount,
                        "purchase_price": purchase_price,
                        "property_address": property_address,
                        "document_paths": []
                    }
                )
                data = response.json()

                if response.status_code != 200:
                    st.error(f"Error: {data.get('detail', 'Unknown error')}")
                else:
                    st.markdown("---")
                    st.markdown("### Compliance Decision")

                    result = data["compliance_result"]
                    if result == "PASS":
                        st.success(f"✅ **{result}** — Application approved")
                    elif result == "FAIL":
                        st.error(f"❌ **{result}** — Application declined")
                    else:
                        st.warning(f"⚠️ **{result}** — Referred for human review")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Confidence Score", f"{data['confidence_score'] * 100:.0f}%")
                    with col2:
                        st.metric("LTV Ratio", data.get("ltv_ratio", "N/A"))
                    with col3:
                        st.metric("Credit Decision", data.get("credit_recommendation", "N/A"))

                    st.markdown("### Compliance Reasons")
                    for reason in data["compliance_reasons"]:
                        st.markdown(f"- {reason}")

                    if data["requires_human_review"]:
                        st.warning("⚠️ This application has been flagged for human underwriter review.")

                    st.markdown("---")
                    st.caption(f"Application ID: {data['application_id']}")

            except Exception as e:
                st.error(f"Failed to connect to the API: {str(e)}")