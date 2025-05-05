import streamlit as st

st.title("AI Job Ad Assistant – Interactive Preview")

st.subheader("📝 Job Title")
st.text_input("Job Title", value="Office Assistant")

st.subheader("🕒 Employment Type")
st.multiselect(
    "Employment Type",
    options=["full-time", "part-time", "internship", "trade licence", "agreement-based"],
    default=["part-time"]
)

st.subheader("📍 Workplace")
st.selectbox(
    "Type of Workplace",
    options=[
        "Work is regularly performed in one workplace",
        "Work at a workplace with optional work from home",
        "Remote work",
        "The job requires travel"
    ],
    index=0
)
st.text_input("Workplace Location", value="Bratislava")

st.subheader("💶 Salary")
col1, col2, col3 = st.columns(3)
col1.number_input("Amount", value=600)
col2.selectbox("Currency", options=["EUR", "CZK", "HUF"], index=0)
col3.selectbox("Time Period", options=["per month", "per hour"], index=0)

st.subheader("🎓 Education Attained")
st.selectbox(
    "Education Level",
    options=[
        "elementary education",
        "secondary school with a GCSE equivalent",
        "secondary school with an A-Levels equivalent",
        "post-secondary technical follow-up / tertiary professional",
        "I. level university degree",
        "II. level university degree",
        "III. level university degree"
    ],
    index=1
)

st.subheader("📄 Job Description")
st.markdown("""
<ul>
  <li>Provide administrative support to the team</li>
  <li>Answer and manage incoming phone calls</li>
  <li>Handle light bookkeeping and filing tasks</li>
  <li>Support daily operations in the office</li>
  <li>You will work 3 days a week, mainly in the mornings</li>
  <li>Your typical day starts with reviewing emails and organizing the agenda</li>
</ul>
""", unsafe_allow_html=True)

st.subheader("🎁 Employee Benefits")
st.markdown("""
<ul>
  <li>You receive meal vouchers for each workday</li>
  <li>You can enjoy flexible working hours that fit your life</li>
  <li>You’ll work in a supportive and friendly team</li>
  <li>Our office is located in the heart of Bratislava</li>
  <li>We offer occasional team events and coffee perks</li>
  <li>You’ll gain experience and responsibility gradually</li>
</ul>
""", unsafe_allow_html=True)

st.subheader("🧠 Personality & Skills")
st.markdown("""
<ul>
  <li>You have completed secondary school</li>
  <li>You are organized and detail-oriented</li>
  <li>You speak and write clearly</li>
  <li>You know basic Excel and MS Office tools</li>
  <li>You enjoy helping others and working on tasks independently</li>
  <li>You are open to learning new administrative systems</li>
</ul>
""", unsafe_allow_html=True)
