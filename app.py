import streamlit as st
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Privacy Policy Lookup", layout="wide")
st.title("🔍 Privacy Policy Lookup")

st.markdown("""
Upload or paste a Privacy Policy and let our app detect potential risks like data sharing, tracking, and lack of consent.
""")

# Input: URL
url = st.text_input("🔗 Paste Privacy Policy URL")

# Input: File Upload
uploaded_file = st.file_uploader("📄 Upload a PDF or TXT file", type=["pdf", "txt"])

# Input: Raw Text
raw_text = st.text_area("📝 Or paste raw privacy policy text", height=200)

# Function: Extract text from PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

# Function: Analyze text for risks
def analyze_text(text):
    flags = []
    risk_score = 0

    rules = {
        "Third-party sharing": r"(share|disclose).{1,20}(third[- ]?part(y|ies)|advertiser|partner)",
        "Collects location": r"(collect|access).{1,20}(location|GPS)",
        "Uses cookies or tracking": r"(cookies|track|analytics)",
        "Biometric data": r"(fingerprint|facial|biometric)",
        "No opt-out": r"(no\s+opt[- ]?out|cannot\s+opt\s+out)",
        "Consent assumption": r"(by using|you agree|deemed to accept)",
        "Financial/ID data": r"(bank|BVN|card number|NIN|passport)",
    }

    for label, pattern in rules.items():
        if re.search(pattern, text, re.IGNORECASE):
            flags.append(label)
            risk_score += 10

    return risk_score, flags

# Function: Extract text from URL (with fallback)
def extract_text_from_url(target_url):
    try:
        res = requests.get(target_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        page_text = soup.get_text().strip()

        # Fallback to Selenium if text is too short
        if len(page_text) < 500:
            st.warning("⚠️ Site may use JavaScript. Trying browser simulation...")

            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(target_url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.quit()
            return soup.get_text().strip()
        return page_text

    except Exception as e:
        st.error(f"❌ Failed to load URL: {e}")
        return ""

# Submit
if st.button("🚀 Analyze"):
    text = ""

    # Load text based on input
    if url:
        text = extract_text_from_url(url)

    elif uploaded_file:
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "text/plain":
            text = uploaded_file.read().decode("utf-8")

    elif raw_text:
        text = raw_text

    if not text:
        st.error("Please provide a valid input (URL, file, or text).")
    else:
        st.success("✅ Privacy policy loaded. Analyzing now...")
        score, detected_flags = analyze_text(text)

        st.subheader("📊 Results")
        st.metric(label="Risk Score", value=f"{score}/100", delta=None)

        if detected_flags:
            st.warning("⚠️ Potential Issues Detected:")
            for flag in detected_flags:
                st.write(f"- {flag}")
        else:
            st.success("✅ No major risks found.")

        st.markdown("---")
        with st.expander("📄 View Full Text"):
            st.text_area("Policy Text", text, height=300)
