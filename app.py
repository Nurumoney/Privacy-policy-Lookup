import streamlit as st
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io

st.set_page_config(page_title="Privacy Policy Lookup", layout="centered")

st.title("🔍 Privacy Policy Lookup")
st.markdown("Analyze privacy policies for potential risks using AI.")

# Input Methods
url = st.text_input("Paste Privacy Policy URL")
uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])
raw_text = st.text_area("Or paste raw privacy policy text")

analyze_button = st.button("🚀 Analyze")

def fetch_policy_from_url(input_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(input_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except Exception as e:
        return f"Error fetching text: {e}"

def extract_text_from_file(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    return ""

def analyze_policy(text):
    lower_text = text.lower()
    risks = []

    sensitive_keywords = [
        "sell your data", "share with third parties", "track your location", 
        "store indefinitely", "targeted ads", "use your contacts", "camera access"
    ]

    for keyword in sensitive_keywords:
        if keyword in lower_text:
            risks.append(f"⚠️ Found keyword: '{keyword}'")

    return risks

if analyze_button:
    final_text = ""

    if url:
        final_text = fetch_policy_from_url(url)
    elif uploaded_file:
        final_text = extract_text_from_file(uploaded_file)
    elif raw_text.strip():
        final_text = raw_text.strip()
    
    if final_text:
        st.success("✅ Privacy Policy extracted.")
        risks = analyze_policy(final_text)

        st.subheader("🧠 Risk Detection Results")
        if risks:
            for r in risks:
                st.error(r)
        else:
            st.success("✅ No major risks detected.")

        st.subheader("📜 Cleaned Policy Text")
        st.text_area("Full Text", value=final_text, height=400)
    else:
        st.error("❌ Please provide a valid input (URL, file, or text).")
