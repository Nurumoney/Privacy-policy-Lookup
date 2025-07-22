import streamlit as st
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader

st.set_page_config(page_title="Privacy Policy Lookup", layout="wide")

def clean_text(text):
    return ' '.join(text.split())

def extract_from_url(url):
    if not url.startswith("http"):
        url = "https://" + url
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return clean_text(soup.get_text())
    except Exception as e:
        return f"Error loading URL: {e}"

def extract_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return clean_text(text)
    elif uploaded_file.type == "text/plain":
        text = uploaded_file.read().decode("utf-8")
        return clean_text(text)
    return "Unsupported file type."

def detect_risks(text):
    risks = []
    if "share with third parties" in text or "third-party" in text:
        risks.append("🔺 May share data with third parties.")
    if "track your activity" in text:
        risks.append("🔺 Tracks user behavior.")
    if "we may collect" in text:
        risks.append("🔺 Collects personal information.")
    if "without your consent" in text:
        risks.append("🔺 Potential consent violation.")
    if not risks:
        risks.append("✅ No major risks detected.")
    return risks

st.title("🛡️ Privacy Policy Lookup")
st.markdown("Upload or paste a Privacy Policy and let our app detect potential risks.")

url_input = st.text_input("🔗 Paste Privacy Policy URL")
uploaded_file = st.file_uploader("📄 Upload a PDF or TXT file", type=["pdf", "txt"])
raw_text = st.text_area("✍️ Or paste raw privacy policy text", height=300)

if st.button("🚀 Analyze"):
    with st.spinner("Analyzing..."):
        policy_text = ""
        if url_input:
            policy_text = extract_from_url(url_input)
        elif uploaded_file:
            policy_text = extract_from_file(uploaded_file)
        elif raw_text:
            policy_text = clean_text(raw_text)

        if not policy_text:
            st.error("Please provide a valid input (URL, file, or text).")
        else:
            st.success("✅ Privacy Policy extracted.")
            st.subheader("🧠 Risk Detection Results")
            for risk in detect_risks(policy_text):
                st.write(risk)

            st.subheader("📜 Cleaned Policy Text")
            st.text_area("Full Text", policy_text, height=300)
