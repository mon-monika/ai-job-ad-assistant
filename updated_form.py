
import streamlit as st
from openai import OpenAI
import json
import os

# Load custom CSS
def load_custom_css(path="form_style.css"):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

# --- Streamlit page setup ---
st.set_page_config(page_title="AI Job Ad Assistant", layout="wide")
st.title("📝 Vytvoriť novú ponuku")

# --- AI Prompt Input Section ---
st.markdown("### 📌 Úvodný popis pozície")
ai_prompt = st.text_area(
    "Opíšte koho hľadáte, čo bude robiť, a čo by mal vedieť alebo mať za sebou",
    placeholder="Napríklad: Hľadáme spoľahlivého skladníka do trojzmennej prevádzky...",
    key="ai_prompt",
)

if st.button("Použiť AI pomocníka"):
    st.session_state["job_title"] = "Skladník (3 zmeny)"
    st.session_state["employment_type"] = ["plný úväzok"]
    st.session_state["workplace_type"] = "na pracovisku"
    st.session_state["workplace_location"] = "Bratislava"
    st.session_state["salary_amount"] = 1200
    st.session_state["salary_currency"] = "EUR"
    st.session_state["salary_period"] = "mesačne"
    st.session_state["education"] = "stredoškolské s maturitou"
    st.session_state["job_description_html"] = "<ul><li>Príjem a výdaj tovaru</li></ul>"
    st.session_state["employee_benefits_html"] = "<ul><li>Stravné lístky</li></ul>"
    st.session_state["personality_prerequisites_and_skills_html"] = "<ul><li>Samostatnosť</li></ul>"

# --- Structured Form Fields ---
st.markdown("### 📄 Informácie o pozícii")

st.text_input("Názov pracovnej pozície", key="job_title")
st.multiselect("Typ pracovného pomeru", ["plný úväzok", "skrátený úväzok", "živnosť", "brigáda", "dohoda"], key="employment_type")

st.radio("Forma výkonu práce", ["na pracovisku", "hybrid", "na diaľku"], key="workplace_type")
st.text_input("Miesto výkonu práce", key="workplace_location")

st.markdown("### 💰 Mzdové podmienky")
col1, col2, col3 = st.columns(3)
with col1:
    st.number_input("Výška mzdy", step=50, key="salary_amount")
with col2:
    st.selectbox("Mena", ["EUR", "CZK"], key="salary_currency")
with col3:
    st.selectbox("Obdobie", ["mesačne", "ročne", "hodinovo"], key="salary_period")

st.selectbox("Dosiahnuté vzdelanie", [
    "základné",
    "stredoškolské bez maturity",
    "stredoškolské s maturitou",
    "vysokoškolské I. stupňa",
    "vysokoškolské II. stupňa",
    "vysokoškolské III. stupňa"
], key="education")

st.markdown("### 🧾 Popis práce")
st.markdown(st.session_state.get("job_description_html", ""), unsafe_allow_html=True)

st.markdown("### 🎁 Benefity")
st.markdown(st.session_state.get("employee_benefits_html", ""), unsafe_allow_html=True)

st.markdown("### 🧠 Požiadavky a zručnosti")
st.markdown(st.session_state.get("personality_prerequisites_and_skills_html", ""), unsafe_allow_html=True)
