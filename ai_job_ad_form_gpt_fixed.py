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
    "follow_up_questions": "",  # Store follow-up questions
    "ai_edited_fields": [],  # Track which fields were edited by AI
    "show_summary": False  # Flag to control when to show the summary
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
    - missing_info: A list of fields that weren't explicitly mentioned in the user's input and required guesswork. For example, if salary wasn't mentioned, include "salary" in this list.

    If any information is not explicitly provided, use your best judgment to create appropriate content for the missing fields, but also include those fields in the missing_info list.
    
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

# --- Generate follow-up questions for missing information ---
def generate_follow_up_questions(missing_fields, job_title):
    if not missing_fields:
        return ""
    
    prompt = f"""
    For a job ad about "{job_title}", I need to collect more information about the following aspects:
    {', '.join(missing_fields)}
    
    Please generate specific questions that would help me gather this missing information from the hiring manager.
    Format the response as a bulleted list with one question per missing field.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using a smaller model for cost efficiency
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating follow-up questions: {e}")
        return "Could not generate follow-up questions. Please provide more details about: " + ", ".join(missing_fields)

# --- Helper function to create field labels with AI indicator ---
def create_field_label(label, field_name):
    if field_name in st.session_state["values"].get("ai_edited_fields", []):
        return f"{label} ✨ <span style='color: #6c757d; font-size: 0.8em;'>Edited by AI</span>"
    return label

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
                # Track which fields were edited by AI
                ai_edited_fields = []
                
                # Store missing fields if provided by the AI
                missing_info = result.get("missing_info", [])
                st.session_state["values"]["missing_fields"] = missing_info
                
                # Update session state with the generated values and track AI edits
                if "job_title" in result and result["job_title"]:
                    st.session_state["values"]["job_title"] = result["job_title"]
                    ai_edited_fields.append("job_title")
                
                if "employment_type" in result and result["employment_type"]:
                    st.session_state["values"]["employment_type"] = result["employment_type"]
                    ai_edited_fields.append("employment_type")
                
                place = result.get("place_of_work", {})
                if place.get("type"):
                    st.session_state["values"]["workplace_type"] = place["type"]
                    ai_edited_fields.append("workplace_type")
                
                if place.get("location"):
                    st.session_state["values"]["workplace_location"] = place["location"]
                    ai_edited_fields.append("workplace_location")
                
                salary = result.get("salary", {})
                if "amount" in salary:
                    st.session_state["values"]["salary_amount"] = salary["amount"]
                    ai_edited_fields.append("salary_amount")
                
                if "currency" in salary:
                    st.session_state["values"]["salary_currency"] = salary["currency"]
                    ai_edited_fields.append("salary_currency")
                
                if "time_period" in salary:
                    st.session_state["values"]["salary_period"] = salary["time_period"]
                    ai_edited_fields.append("salary_period")
                
                if "education_attained" in result and result["education_attained"]:
                    st.session_state["values"]["education"] = result["education_attained"]
                    ai_edited_fields.append("education")

                # Clean HTML tags and show plain text with bullet points
                if "job_description_html" in result and result["job_description_html"]:
                    st.session_state["values"]["job_description_html"] = "\n".join(
                        [f"- {item.strip()}</li>" for item in result.get("job_description_html", "").split("<li>")[1:]]
                    ).replace("</li>", "")
                    ai_edited_fields.append("job_description_html")

                if "employee_benefits_html" in result and result["employee_benefits_html"]:
                    st.session_state["values"]["employee_benefits_html"] = "\n".join(
                        [f"- {item.strip()}</li>" for item in result.get("employee_benefits_html", "").split("<li>")[1:]]
                    ).replace("</li>", "")
                    ai_edited_fields.append("employee_benefits_html")

                if "personality_prerequisites_and_skills_html" in result and result["personality_prerequisites_and_skills_html"]:
                    st.session_state["values"]["personality_prerequisites_and_skills_html"] = "\n".join(
                        [f"- {item.strip()}</li>" for item in result.get("personality_prerequisites_and_skills_html", "").split("<li>")[1:]]
                    ).replace("</li>", "")
                    ai_edited_fields.append("personality_prerequisites_and_skills_html")
                
                # Save the list of AI-edited fields
                st.session_state["values"]["ai_edited_fields"] = ai_edited_fields
                
                # Set flag to show summary
                st.session_state["values"]["show_summary"] = True
                
                # If there are missing fields, generate follow-up questions
                if missing_info:
                    job_title = result.get("job_title", "this position")
                    follow_up_questions = generate_follow_up_questions(missing_info, job_title)
                    st.session_state["values"]["follow_up_questions"] = follow_up_questions
                
                # Force a rerun to show the summary
                st.rerun()
        else:
            st.warning("Please enter a prompt before generating.")

# --- Display AI Generation Summary (outside of the expander) ---
if st.session_state["values"].get("show_summary", False):
    st.success("✨ AI has generated content for your job ad!")
    
    # Create a summary of what was generated
    st.markdown("### What AI Generated:")
    
    summary_items = []
    ai_edited_fields = st.session_state["values"].get("ai_edited_fields", [])
    
    # Map field names to user-friendly labels
    field_labels = {
        "job_title": "Job Title",
        "employment_type": "Employment Type",
        "workplace_type": "Workplace Type",
        "workplace_location": "Workplace Location",
        "salary_amount": "Salary Amount",
        "salary_currency": "Salary Currency",
        "salary_period": "Salary Period",
        "education": "Education Required",
        "job_description_html": "Job Description",
        "employee_benefits_html": "Employee Benefits",
        "personality_prerequisites_and_skills_html": "Required Skills & Personality"
    }
    
    # Create summary list
    for field in ai_edited_fields:
        if field in field_labels:
            value = st.session_state["values"].get(field, "")
            if isinstance(value, list):
                value = ", ".join(value)
            summary_items.append(f"- **{field_labels[field]}**: {value[:50]}{'...' if len(str(value)) > 50 else ''}")
    
    if summary_items:
        st.markdown("\n".join(summary_items))
    
    # Display follow-up questions if there are missing fields
    if st.session_state["values"].get("follow_up_questions"):
        st.markdown("### Follow-up Questions:")
        st.markdown(st.session_state["values"]["follow_up_questions"])
        st.markdown("---")
    
    # Add a button to clear the summary
    if st.button("Clear Summary"):
        st.session_state["values"]["show_summary"] = False
        st.rerun()
