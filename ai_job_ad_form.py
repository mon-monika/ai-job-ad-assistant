import streamlit as st

st.set_page_config(page_title="AI Job Ad Assistant", layout="centered")

st.title("📝 Job Ad Form")

# Session state to store values across reruns
if "prefilled" not in st.session_state:
    st.session_state.prefilled = False
    st.session_state.values = {
        "job_title": "",
        "employment_type": [],
        "workplace_type": "",
        "workplace_location": "",
        "salary_amount": 0,
        "salary_currency": "EUR",
        "salary_period": "per month",
        "education": ""
    }

# Simulated AI output for testing
def generate_from_prompt(prompt):
    return {
        "job_title": "Office Assistant",
        "employment_type": ["part-time"],
        "workplace_type": "Work is regularly performed in one workplace",
        "workplace_location": "Bratislava",
        "salary_amount": 600,
        "salary_currency": "EUR",
        "salary_period": "per month",
        "education": "secondary school with a GCSE equivalent"
    }

# --- AI Section ---
with st.expander("✨ Use AI to prefill the form"):
    user_prompt = st.text_area(
        "Describe the position (freeform):",
        placeholder="We’re hiring a part-time office assistant in Bratislava..."
    )
    if st.button("Generate with AI"):
        if user_prompt.strip():
            result = generate_from_prompt(user_prompt)
            st.session_state.values = result
            st.session_state.prefilled = True
        else:
            st.warning("Please enter a prompt before generating.")

st.divider()
st.subheader("📄 Job Ad Form")

# --- Job Ad Form Inputs ---
st.session_state.values["job_title"] = st.text_input("Job Title", st.session_state.values["job_title"])

st.session_state.values["employment_type"] = st.multiselect(
    "Employment Type",
    ["full-time", "part-time", "internship", "trade licence", "agreement-based"],
    default=st.session_state.values["employment_type"]
)

st.session_state.values["workplace_type"] = st.selectbox(
    "Workplace Type",
    ["", "Work is regularly performed in one workplace", "Work at a workplace with optional work from home", "Remote work", "The job requires travel"],
    index=0 if not st.session_state.values["workplace_type"] else ["", "Work is regularly performed in one workplace", "Work at a workplace with optional work from home", "Remote work", "The job requires travel"].index(st.session_state.values["workplace_type"])
)

st.session_state.values["workplace_location"] = st.text_input("Workplace Location", st.session_state.values["workplace_location"])

col1, col2, col3 = st.columns(3)
st.session_state.values["salary_amount"] = col1.number_input("Salary Amount", value=st.session_state.values["salary_amount"])
st.session_state.values["salary_currency"] = col2.selectbox("Currency", ["EUR", "CZK", "HUF"], index=["EUR", "CZK", "HUF"].index(st.session_state.values["salary_currency"]))
st.session_state.values["salary_period"] = col3.selectbox("Salary Period", ["per month", "per hour"], index=["per month", "per hour"].index(st.session_state.values["salary_period"]))

st.session_state.values["education"] = st.selectbox(
    "Education Attained",
    [
        "", "elementary education", "secondary school with a GCSE equivalent",
        "secondary school with an A-Levels equivalent",
        "post-secondary technical follow-up / tertiary professional",
        "I. level university degree", "II. level university degree", "III. level university degree"
    ],
    index=0 if not st.session_state.values["education"] else [
        "", "elementary education", "secondary school with a GCSE equivalent",
        "secondary school with an A-Levels equivalent",
        "post-secondary technical follow-up / tertiary professional",
        "I. level university degree", "II. level university degree", "III. level university degree"
    ].index(st.session_state.values["education"])
)

st.divider()

if st.button("✅ Submit"):
    st.success("Form submitted successfully!")
    st.json(st.session_state.values)
