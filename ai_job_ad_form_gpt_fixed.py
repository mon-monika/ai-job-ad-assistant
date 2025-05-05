import streamlit as st
import openai
import os
import json

# Load API key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
    "education": ""
}

if "values" not in st.session_state:
    st.session_state["values"] = default_values.copy()
else:
    for key, default in default_values.items():
        if key not in st.session_state["values"]:
            st.session_state["values"][key] = default

# --- Real GPT-4 call ---
def generate_from_prompt(prompt_text, field_type):
    system_prompt = """
You are assisting a recruiter by generating a structured job ad based on freeform input. Based on the provided text:
    
- job_title
- employment_type: full-time, part-time, internship, trade licence, agreement-based (1 or more)
- place_of_work:
    • type: one of: "Work is regularly performed in one workplace", "Work at a workplace with optional work from home", "Remote work", "The job requires travel"
    • location: if needed
- salary: amount (numeric, pick the midpoint or lower value if a range is given), currency (EUR, CZK, HUF), and time_period ("per month", "per hour")
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
    user_prompt = ""
    if field_type == "job_title":
        user_prompt = f"You are an experienced HR manager in a company that wants to fill the position of {prompt_text}. Come up with a headline for a job advertisement to be posted on a job portal. The character count for each headline is a maximum of 60. The language is English. You must not use an exclamation mark."
    elif field_type == "job_description":
        user_prompt = f"Formulate in a minimum of 6 points the job description and activities typical for the position of {prompt_text}. Address the job applicant using the formal 'you' in the present tense. The tone of the text should be friendly and informal."
    elif field_type == "benefits":
        user_prompt = f"Formulate in 6 sentences typical company benefits that will interest applicants for the job position {prompt_text}. Adjust your benefit suggestions for the job position in Slovakia, but keep the output in English. The tone of the text is friendly and informal."
    elif field_type == "skills":
        user_prompt = f"Formulate in 6 short sentences typical skills and education required for the position of {prompt_text}. The tone of the text is friendly and informal. Put each skill on a separate line. Always return the text as an HTML list."

    client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4
    )
    raw_text = response.choices[0].message.content
    try:
        return raw_text
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
            # Generate job title
            job_title = generate_from_prompt(user_prompt, "job_title")
            st.session_state["values"]["job_title"] = job_title

            # Generate job description
            job_description = generate_from_prompt(user_prompt, "job_description")
            st.session_state["values"]["job_description"] = job_description

            # Generate employee benefits
            benefits = generate_from_prompt(user_prompt, "benefits")
            st.session_state["values"]["benefits"] = benefits

            # Generate skills
            skills = generate_from_prompt(user_prompt, "skills")
            st.session_state["values"]["skills"] = skills

            # Populate the form with results
            st.write(f"**Job Title:** {job_title}")
            st.write(f"**Job Description:** {job_description}")
            st.write(f"**Benefits:** {benefits}")
            st.write(f"**Skills and Education:** {skills}")
        else:
            st.warning("Please enter a prompt before generating.")

st.markdown("---")
st.subheader("📄 Job Ad Form")

# --- Job Ad Form Inputs ---
st.session_state["values"]["job_title"] = st.text_input("Job Title", st.session_state["values"]["job_title"])

st.session_state["values"]["employment_type"] = st.multiselect(
    "Employment Type",
    ["full-time", "part-time", "internship", "trade licence", "agreement-based"],
    default=st.session_state["values"]["employment_type"]
)

st.session_state["values"]["workplace_type"] = st.selectbox(
    "Workplace Type",
    ["", "Work is regularly performed in one workplace", "Work at a workplace with optional work from home", "Remote work", "The job requires travel"],
    index=0 if not st.session_state["values"]["workplace_type"] else ["", "Work is regularly performed in one workplace", "Work at a workplace with optional work from home", "Remote work", "The job requires travel"].index(st.session_state["values"]["workplace_type"])
)

st.session_state["values"]["workplace_location"] = st.text_input("Workplace Location", st.session_state["values"]["workplace_location"])

col1, col2, col3 = st.columns(3)
try:
    salary_value = float(st.session_state["values"].get("salary_amount", 0.0))
except (TypeError, ValueError):
    salary_value = 0.0
st.session_state["values"]["salary_amount"] = col1.number_input("Salary Amount", value=salary_value)
st.session_state["values"]["salary_currency"] = col2.selectbox("Currency", ["EUR", "CZK", "HUF"], index=["EUR", "CZK", "HUF"].index(st.session_state["values"]["salary_currency"]))
st.session_state["values"]["salary_period"] = col3.selectbox("Salary Period", ["per month", "per hour"], index=["per month", "per hour"].index(st.session_state["values"]["salary_period"]))

st.session_state["values"]["education"] = st.selectbox(
    "Education Attained",
    [
        "", "elementary education", "secondary school with a GCSE equivalent",
        "secondary school with an A-Levels equivalent",
        "post-secondary technical follow-up / tertiary professional",
        "I. level university degree", "II. level university degree", "III. level university degree"
    ],
    index=0 if not st.session_state["values"]["education"] else [
        "", "elementary education", "secondary school with a GCSE equivalent",
        "secondary school with an A-Levels equivalent",
        "post-secondary technical follow-up / tertiary professional",
        "I. level university degree", "II. level university degree", "III. level university degree"
    ].index(st.session_state["values"]["education"])
)
st.session_state["values"]["job_description"] = st.text_area("Job Description", st.session_state["values"].get("job_description", ""))
st.session_state["values"]["benefits"] = st.text_area("Employee Benefits", st.session_state["values"].get("benefits", ""))
st.session_state["values"]["skills"] = st.text_area("Skills and Education", st.session_state["values"].get("skills", ""))


st.markdown("---")

if st.button("✅ Submit"):
    st.success("Form submitted successfully!")
    st.json(st.session_state["values"])
