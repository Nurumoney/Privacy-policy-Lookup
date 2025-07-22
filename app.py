import streamlit as st
import fitz  # PyMuPDF for PDF
import requests
from bs4 import BeautifulSoup

st.title("🔍 Privacy Policy Lookup")

# URL Input
url = st.text_input("Paste a URL to a privacy policy")

# File Upload
uploaded_file = st.file_uploader("Upload PDF or TXT file", type=["pdf", "txt"])

# Raw Text Input
raw_text = st.text_area("Or paste raw privacy policy text")

# Process Button
if st.button("Analyze"):
    text = ""

    if url:
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            text = soup.get_text()
        except:
            st.error("Failed to fetch from URL")

    elif uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            pdf_doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = "\n".join([page.get_text() for page in pdf_doc])
        elif uploaded_file.type == "text/plain":
            text = uploaded_file.read().decode("utf-8")

    elif raw_text:
        text = raw_text

    if text:
        st.success("Policy loaded successfully! Running analysis...")

        # Placeholder for AI analysis (replace with your actual model)
        st.write("**Key findings:**")
        st.write("- Data collection detected")
        st.write("- Location access found")
        st.write("- Policy mentions third-party sharing")
        st.warning("⚠️ Risk score: 67/100 (Medium Risk)")
    else:
        st.error("Please provide some input to analyze.")
