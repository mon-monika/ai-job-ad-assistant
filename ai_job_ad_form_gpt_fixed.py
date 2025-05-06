import streamlit as st
from openai import OpenAI
import json

# Create OpenAI client with API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.set_page_config(page_title="AI Job Ad Assistant", layout="centered")
st.title("📝 Job Ad Form")

# --- Robust session state initialization ---
default_values = {
    "job_title": "",
    "employment_type": [],
    "workplace_type": "",
    "workplace_location": "",
    "salary_amount": 0,
    "salary_currency": "EUR",
    "salary_period": "per month",
    "education": "",
    "job_description_html": "",
    "employee_benefits_html": "",
    "personality_prerequisites_and_skills_html": "",
    "job_title_variants": {"friendly": ""},
    "missing_fields": [],  # Track missing fields
    "follow_up_questions": ""  # Store follow-up questions
}

if "values" not in st.session_state:
    st.session_state["values"] = default_values.copy()
else:
    for key, default in default_values.items():
        if key not in st.session_state["values"]:
            st.session_state["values"][key] = default