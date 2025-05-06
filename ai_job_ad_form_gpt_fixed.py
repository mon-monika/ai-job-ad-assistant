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
    "education": "",
    "job_description_html": "",
    "employee_benefits_html": "",
    "personality_prerequisites_and_skills_html": "",
    "job_title_variants": {"friendly": ""}
}

if "values" not in st.session_state:
    st.session_state["values"] = default_values.copy()
else:
    for key, default in default_values.items():
        if key not in st.session_state["values"]:
            st.session_state["values"][key] = default

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
    - salary: amount (numeric, pick the midpoint or lower value if a range is given), currency (EUR, CZK, HUF), and time_period ("per month", "per hour")
    - education_attained: one of:
      "elementary education",
      "secondary school with a GCSE equivalent",
      "secondary school with an A-Levels equivalent",
      "post-secondary technical follow-up / tertiary professional",
      "I. level university degree",
      "II. level university degree",
      "III. level university degree"
    Then generate the following content in a structured JSON format:
    - job_title: A single creative and friendly job ad headline (max 60 characters, no exclamation marks)
    - job_description_html: A <ul> list with at least 6 bullet points, each item representing a specific responsibility or task.
    - employee_benefits_html: A <ul> list with 6 friendly, engaging benefit sentences tailored to jobs in Slovakia.
    - personality_prerequisites_and_skills_html: A <ul> list with 6 short lines describing required education, soft and hard skills.
    Return everything as a JSON object with these keys:
    {
      "job_title": "",
      "employment_type": [],
      "place_of_work": {
        "type": "",
        "location": ""
      },
      "salary": {
        "amount": null,
        "currency": "",
        "time_period": ""
      },
      "education_attained": "",
      "job_description_html": "<ul><li>...</li></ul>",
      "employee_benefits_html": "<ul><li>...</li></ul>",
      "personality_prerequisites_and_skills_html": "<ul><li>...</li></ul>"
    }
    """
    user_prompt = f"Here is the job description: {prompt_text}"

    try:
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )

        # Debug: Print the raw response from the AI
        raw_text = response.choices[0].message.content
        st.write("Raw AI response:", raw_text)  # This will display the raw response for debugging
    
# Attempt to extract the JSON part from the response
try:
        if "```json" in raw_text and "```" in raw_text:
            json_string = raw_text.split("```json\n")[1].split("\n```")[0]  # Extract the JSON part
            job_ad = json.loads(json_string)  # Parse the extracted JSON string
            return job_ad
        else:
            st.error("AI response does not contain the expected JSON format.")
            st.write("Raw response:", raw_text)
            return {}

        except Exception as e:
            st.error(f"Error parsing AI output: {e}")
            st.write("Raw response:", raw_text)
            return {}

    except Exception as e:
        st.error(f"An error occurred: {e}")
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
                st.session_state["values"]["job_title"] = result.get("job_title", "")
                st.session_state["values"]["employment_type"] = result.get("employment_type", [])
                place = result.get("place_of_work", {})
                st.session_state["values"]["workplace_type"] = place.get("type", "")
                st.session_state["values"]["workplace_location"] = place.get("location", "")
                salary = result.get("salary", {})
                st.session_state["values"]["salary_amount"] = salary.get("amount", 0)
                st.session_state["values"]["salary_currency"] = salary.get("currency", "EUR")
                st.session_state["values"]["salary_period"] = salary.get("time_period", "per month")
                st.session_state["values"]["education"] = result.get("education_attained", "")

                # Clean HTML tags and show plain text with bullet points
                st.session_state["values"]["job_description_html"] = "\n".join(
                    [f"- {item.strip()}</li>" for item in result.get("job_description_html", "").split("<li>")[1:]]
                ).replace("</li>", "")

                st.session_state["values"]["employee_benefits_html"] = "\n".join(
                    [f"- {item.strip()}</li>" for item in result.get("employee_benefits_html", "").split("<li>")[1:]]
                ).replace("</li>", "")

                st.session_state["values"]["personality_prerequisites_and_skills_html"] = "\n".join(
                    [f"- {item.strip()}</li>" for item in result.get("personality_prerequisites_and_skills_html", "").split("<li>")[1:]]
                ).replace("</li>", "")
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

st.markdown("---")

# Only show the editable text areas for job description, benefits, and skills
st.subheader("📄 Job Description")
st.session_state["values"]["job_description_html"] = st.text_area(
    "Generated Job Description", 
    value=st.session_state["values"].get("job_description_html", ""), 
    height=180
)

st.subheader("🎁 Employee Benefits")
st.session_state["values"]["employee_benefits_html"] = st.text_area(
    "Generated Benefits", 
    value=st.session_state["values"].get("employee_benefits_html", ""), 
    height=150
)

st.subheader("🧠 Personality & Skills")
st.session_state["values"]["personality_prerequisites_and_skills_html"] = st.text_area(
    "Generated Skills", 
    value=st.session_state["values"].get("personality_prerequisites_and_skills_html", ""), 
    height=150
)

if st.button("✅ Submit"):
    st.success("Form submitted successfully!")
    st.json(st.session_state["values"])
