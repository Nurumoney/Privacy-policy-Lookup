import streamlit as st
from summarizer import generate_summary
from analyzer import analyze_text
from utils.pdf_reader import extract_text_from_pdf
from utils.url_scraper import extract_text_from_url

st.set_page_config(page_title="Privacy Policy Lookup", layout="wide")

st.title("🔍 Privacy Policy Lookup")
st.markdown("AI-powered analyzer to help you understand and flag hidden risks in privacy policies and user agreements.")

st.sidebar.header("Input Method")
input_method = st.sidebar.radio("Choose how you want to upload the policy", ["Paste Text", "Upload File", "Enter URL"])

input_text = ""

# Handle input methods
if input_method == "Paste Text":
    input_text = st.text_area("Paste the privacy policy text here:", height=300)

elif input_method == "Upload File":
    uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])
    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            input_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith(".txt"):
            input_text = uploaded_file.read().decode("utf-8")

elif input_method == "Enter URL":
    url = st.text_input("Enter the URL of the privacy policy:")
    if url:
        input_text = extract_text_from_url(url)

# Display and process
if input_text:
    st.subheader("🔎 AI Summary")
    with st.spinner("Summarizing..."):
        summary = generate_summary(input_text)
        st.success("Done!")
        st.write(summary)

    st.subheader("⚠️ Risk Analysis")
    with st.spinner("Scanning for potential red flags..."):
        flagged_issues = analyze_text(input_text)
        if flagged_issues:
            for issue in flagged_issues:
                st.warning(f"⚠️ {issue}")
        else:
            st.success("No major risks detected.")
