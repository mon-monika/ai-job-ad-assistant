import streamlit as st
import openai
import os
import json

# Load API key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="AI Job Ad Assistant", layout="centered")
st.title("📝 Job Ad Form")

# --- Initialize session state safely ---
if "values" not in st.session_state:
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

# --- Real GPT-4 call ---
def generate_from_prompt(prompt_text):
    system_prompt = """
You are assisting a recruiter by generating a structured job ad based on freeform input. Based on the provided text:

Extract these fields:
- job_title
- employment_type: full-time, part-time, internship, trade licence, agreement-based (1 or more)
- place_of_work:
    • type: one of: "Work is regularly performed in one workplace", "Work at a workplace with optional work from home", "Remote work", "The job requires travel"
    • location: if needed
- salary: amount (numeric), currency (EUR, CZK, HUF), and time_period ("per month", "per hour")
- education_attained: one of:
  "elementary education",
  "secondary school with a GCSE equivalent",
  "secondary school with an A-Levels equivalent",
  "post-secondary technical follow-up / tertiary professional",
  "I. level university degree",
  "II. level university degree",
  "III. level university degree"

Return this as a JSON object.
"""

    user_prompt = f"Here is the job description: {prompt_text}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4
    )

    raw_text = response.choices[0].message["content"]
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        st.error("⚠️ AI output could not be parsed. Try rewording your prompt.")
        return {}

# --- AI Section ---
with st.expander("✨ Use AI to prefill the form"):
    user_prompt = st.text_area(
        "Describe the position (freeform):",
        placeholder="We’re hiring a part-time office assistant in Bratislava..."
    )
    if st.button("Generate with AI"):
        if user_prompt.strip():
            result = generate_from_prompt(user_prompt)
            if result:
                st.session_state.values["job_title"] = result.get("job_title", "")
                st.session_state.values["employment_type"] = result.get("employment_type", [])
                place = result.get("place_of_work", {})
                st.session_state.values["workplace_type"] = place.get("type", "")
                st.session_state.values["workplace_location"] = place.get("location", "")
                salary = result.get("salary", {})
                st.session_state.values["salary_amount"] = salary.get("amount", 0)
                st.session_state.values["salary_currency"] = salary.get("currency", "EUR")
                st.session_state.values["salary_period"] = salary.get("time_period", "per month")
                st.session_state.values["education"] = result.get("education_attained", "")
        else:
            st.warning("Please enter a prompt before generating.")

st.markdown("---")
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

st.markdown("---")

if st.button("✅ Submit"):
    st.success("Form submitted successfully!")
    st.json(st.session_state.values)
