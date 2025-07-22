import streamlit as st
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io

st.set_page_config(page_title="Privacy Policy Lookup", layout="wide")
st.title("🔍 Privacy Policy Lookup with AI Summary")

# --- Helper Functions ---
def analyze_policy(text):
    lower_text = text.lower()
    risks = []
    suspicious_lines = []

    sensitive_keywords = [
        "sell your data", "share with third parties", "track your location",
        "store indefinitely", "targeted ads", "use your contacts", "camera access",
        "read your sms", "microphone access", "collect device information"
    ]

    lines = text.split('\n')
    for line in lines:
        lower_line = line.lower()
        for keyword in sensitive_keywords:
            if keyword in lower_line:
                risks.append(f"⚠️ Found keyword: '{keyword}'")
                suspicious_lines.append(line.strip())

    return risks, suspicious_lines

def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"Failed to fetch: {e}"

# --- Sidebar Input Selection ---
st.sidebar.header("Input Options")
source_option = st.sidebar.radio("Select input source:", ["Paste Text", "Upload PDF", "Enter URL"])

final_text = ""

# --- User Input Logic ---
if source_option == "Paste Text":
    raw_text = st.text_area("📋 Paste the privacy policy text here:", height=300)
    if st.button("Analyze"):
        final_text = raw_text

elif source_option == "Upload PDF":
    uploaded_file = st.file_uploader("📄 Upload a Privacy Policy PDF", type=["pdf"])
    if uploaded_file and st.button("Analyze"):
        final_text = extract_text_from_pdf(uploaded_file)

elif source_option == "Enter URL":
    url = st.text_input("🌐 Enter URL to a privacy policy:")
    if st.button("Analyze"):
        final_text = extract_text_from_url(url)

# --- Analysis Section ---
if final_text:
    st.subheader("📑 Raw Extracted Text")
    with st.expander("Click to view full policy text"):
        st.write(final_text[:5000])  # Preview first 5000 characters

    # AI Summary Placeholder (static for now)
    st.subheader("🧠 AI Summary")
    st.info("This policy appears to contain standard clauses. Be cautious of terms like third-party sharing or location tracking.")

    # Run detection
    risks, suspicious_lines = analyze_policy(final_text)

    st.subheader("🚨 Risk Detection Results")
    if risks:
        for risk in risks:
            st.error(risk)
    else:
        st.success("✅ No major risk keywords detected.")

    # Show lines where they appear
    if suspicious_lines:
        st.subheader("🔎 Lines Containing Suspicious Language")
        for line in suspicious_lines:
            st.code(line, language="markdown")
