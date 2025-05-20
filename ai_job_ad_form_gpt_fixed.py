import streamlit as st
from openai import OpenAI
import json

# Inject custom CSS
def load_custom_css(path="form_styles.css"):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()


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
    You are assisting a recruiter by generating a structured job ad based on freeform input. Based on the provided text, return the following in **valid JSON format** without any introduction or explanation text.
    
    Your response MUST include ALL of these fields:
    
    - job_title: You are an experienced HR manager in a company that wants to fill the position of a %s. Come up with a friendly and motivational headline for a job advertisement to be posted on a job portal. The character count for each headline is a maximum of 60. The language is English. You must not use an exclamation mark. 
    - employment_type: full-time, part-time, internship, trade licence, agreement-based (1 or more)
    - place_of_work:
        • type: one of: "Work is regularly performed in one workplace", "Work at a workplace with optional work from home", "Remote work", "The job requires travel"
        • location: if needed
    - salary: amount (numeric, pick the midpoint or lower value if a range is given), currency (EUR, CZK, HUF), and time_period ("per month", "per hour")
    - education_attained: one of:
        "elementary education", "secondary school with a GCSE equivalent", "secondary school with an A-Levels equivalent", "post-secondary technical follow-up / tertiary professional", "I. level university degree", "II. level university degree", "III. level university degree"
    - job_description_html: A detailed HTML list. Formulate in a minimum of 6 points the job description and activities typical for the position of %s. Address the job applicant using the formal "you" in the present tense (Example: You will operate machines). The tone of the text should be friendly and informal. Describe a typical day in the job position, maximum of 2 points. Describe the typical working hours for the position, maximum of 2 points. of job responsibilities and tasks (<ul><li>item</li></ul> format)
    - employee_benefits_html: A detailed HTML list. Formulate in 6 sentences typical company benefits that will interest applicants for the job position %s. Adjust your benefit suggestions for the job position in Slovakia, but keep the output in English. The tone of the text is friendly and informal, in the second person singular (Example: You can receive a contribution). Make a list and write longer and interesting sentences. Omit introductory and concluding sentences. (<ul><li>item</li></ul> format)
    - personality_prerequisites_and_skills_html: A detailed HTML list. Formulate in 6 short sentences typical skills and education required for the position of %s. The tone of the text is friendly and informal, in the second person plural (Example: You speak English). Specify the typically required education type, hard skills, and soft skills. Put each skill on a separate line. (<ul><li>item</li></ul> format)

    If any information is not explicitly provided, use your best judgment to create appropriate content for the missing fields.
    
    Return ONLY the JSON object without any explanatory text before or after it.
    """
    user_prompt = f"Here is the job description: {prompt_text}"

    try:
        # Updated OpenAI API call for version 1.0.0+
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1500,
            temperature=0.4
        )

        raw_text = response.choices[0].message.content.strip()  # Extracting text from the response
        # st.write("Raw AI response:", raw_text)  # Debug: Print the raw response from the AI - commented out
        try:
            # Try to extract just the JSON part if there's explanatory text
            # Look for the first '{' and the last '}'
            json_start = raw_text.find('{')
            json_end = raw_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = raw_text[json_start:json_end]
                job_ad = json.loads(json_text)  # Parse the JSON string
                
                # Check for missing fields
                required_fields = [
                    "job_description_html", 
                    "employee_benefits_html", 
                    "personality_prerequisites_and_skills_html"
                ]
                
                missing_fields = [field for field in required_fields if field not in job_ad]
                if missing_fields:
                    st.warning(f"The AI response is missing these fields: {', '.join(missing_fields)}. Generating them now...")
                    
                    # Make a second API call to generate the missing fields
                    completion_prompt = f"""
                    Based on this job information:
                    
                    Job Title: {job_ad.get('job_title', '')}
                    Employment Type: {', '.join(job_ad.get('employment_type', []))}
                    Workplace: {job_ad.get('place_of_work', {}).get('type', '')} in {job_ad.get('place_of_work', {}).get('location', '')}
                    Salary: {job_ad.get('salary', {}).get('amount', '')} {job_ad.get('salary', {}).get('currency', '')} {job_ad.get('salary', {}).get('time_period', '')}
                    Education: {job_ad.get('education_attained', '')}
                    
                    Generate the following in valid JSON format:
                    
                    {{
                        "job_description_html": "<ul><li>detailed job responsibilities</li><li>...</li></ul>",
                        "employee_benefits_html": "<ul><li>benefits offered</li><li>...</li></ul>",
                        "personality_prerequisites_and_skills_html": "<ul><li>required skills</li><li>...</li></ul>"
                    }}
                    
                    Be creative and detailed. Return ONLY the JSON object.
                    """
                    
                    completion_response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": completion_prompt}],
                        max_tokens=1000,
                        temperature=0.5
                    )
                    
                    completion_text = completion_response.choices[0].message.content.strip()
                    
                    # Extract JSON from the completion response
                    comp_json_start = completion_text.find('{')
                    comp_json_end = completion_text.rfind('}') + 1
                    
                    if comp_json_start >= 0 and comp_json_end > comp_json_start:
                        completion_json = json.loads(completion_text[comp_json_start:comp_json_end])
                        
                        # Update the job_ad with the missing fields
                        for field in missing_fields:
                            if field in completion_json:
                                job_ad[field] = completion_json[field]
                
                return job_ad
            else:
                # If we can't find JSON markers, try parsing the whole thing
                job_ad = json.loads(raw_text)
                return job_ad
                
        except json.JSONDecodeError as e:
            st.error(f"⚠️ AI output could not be parsed. Error: {e}. Raw response: {raw_text}")
            return {}

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return {}

# --- AI Section ---
with st.expander("✨ Use AI to prefill the form"):
    user_prompt = st.text_area(
        "Describe the position (freeform):",
        placeholder="We're hiring a part-time office assistant in Bratislava..."
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

result = None
# --- Summary Section ---  

def job_ad_summary_list(job_ad):
    summary_lines = []

    # Job Title
    if job_ad.get("job_title"):
        summary_lines.append(f"- **Job Title:** {job_ad['job_title']}")

    # Salary
    salary = job_ad.get("salary", {})
    if salary and salary.get("amount"):
        salary_str = f"{salary['amount']} {salary.get('currency', '')} per {salary.get('time_period', '')}"
        summary_lines.append(f"- **Salary:** {salary_str}")

    # Employment Type
    if job_ad.get("employment_type"):
        summary_lines.append(f"- **Employment Type:** {', '.join(job_ad['employment_type'])}")

    # Workplace
    place = job_ad.get("place_of_work", {})
    if place and place.get("type"):
        location = place.get("location", "")
        summary_lines.append(f"- **Workplace:** {place['type']} in {location}")

    # Education
    if job_ad.get("education_attained"):
        summary_lines.append(f"- **Education:** {job_ad['education_attained']}")

    # Job Description
    if job_ad.get("job_description_html"):
        summary_lines.append("- **Job Description:** (has been edited)")

    return "\n".join(summary_lines)

if result:
    summary_md = job_ad_summary_list(result)
    st.markdown("### AI-Filled Fields Overview")
    st.markdown(summary_md)


# --- Job Ad Form Inputs ---
st.session_state["values"]["job_title"] = st.text_input(
    "Job Title", st.session_state["values"].get("job_title", "")
)

st.session_state["values"]["employment_type"] = st.multiselect(
    "Employment Type",
    ["full-time", "part-time", "internship", "trade licence", "agreement-based"],
    default=st.session_state["values"].get("employment_type", [])
)

st.session_state["values"]["workplace_type"] = st.selectbox(
    "Workplace Type",
    ["", "Work is regularly performed in one workplace", "Work at a workplace with optional work from home", "Remote work", "The job requires travel"],
    index=0 if not st.session_state["values"]["workplace_type"] else ["", "Work is regularly performed in one workplace", "Work at a workplace with optional work from home", "Remote work", "The job requires travel"].index(st.session_state["values"]["workplace_type"])
)

st.session_state["values"]["workplace_location"] = st.text_input(
    "Workplace Location", st.session_state["values"].get("workplace_location", "")
)

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
