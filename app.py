import streamlit as st
import requests
from bs4 import BeautifulSoup
import PyPDF2
from gtts import gTTS
import tempfile

# Offline ML summarization
import nltk
import os
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

# --- NLTK Tokenizer Download Fix ---
nltk_path = os.path.join(os.getcwd(), "nltk_data")
os.makedirs(nltk_path, exist_ok=True)
nltk.download("punkt", download_dir=nltk_path)
nltk.data.path.append(nltk_path)

# --- Streamlit Page Config ---
st.set_page_config(page_title="Privacy Policy Lookup", layout="wide")
st.title("🔍 Privacy Policy Lookup (Offline AI Summary)")

# --- Functions ---
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
        if page.extract_text():
            text += page.extract_text()
    return text

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"Failed to fetch: {e}"

def summarize_with_local_model(text, sentence_count=5):
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = TextRankSummarizer()
        summary = summarizer(parser.document, sentence_count)
        return " ".join(str(sentence) for sentence in summary)
    except Exception as e:
        return f"❌ Local summary failed: {e}"

def generate_voice(summary_text, lang_code):
    try:
        short_text = summary_text[:500]
        tts = gTTS(short_text, lang=lang_code)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        st.error(f"Text-to-speech failed: {e}")
        return None

# --- Sidebar Input ---
st.sidebar.header("Input Options")
source_option = st.sidebar.radio("Select input source:", ["Paste Text", "Upload PDF", "Enter URL"])
final_text = ""

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

# --- Main Processing ---
if final_text:
    st.subheader("📑 Extracted Policy Text")
    with st.expander("Click to view raw text"):
        st.write(final_text[:5000])

    st.subheader("🧠 AI Summary (Offline TextRank)")
    with st.spinner("Generating summary..."):
        ai_summary = summarize_with_local_model(final_text)
    st.info(ai_summary)

    st.subheader("🎧 Hear the Summary in a Local Language")
    language_choice = st.selectbox("Choose a language:", ["None", "Hausa", "Yoruba"])
    lang_codes = {"Hausa": "ha", "Yoruba": "yo"}

    if language_choice in lang_codes:
        lang_code = lang_codes[language_choice]
        with st.spinner(f"Generating audio in {language_choice}..."):
            audio_path = generate_voice(ai_summary, lang_code)
        if audio_path:
            st.audio(audio_path, format="audio/mp3")
        else:
            st.warning("Audio generation failed.")

    st.subheader("🚨 Risk Detection Results")
    risks, suspicious_lines = analyze_policy(final_text)
    if risks:
        for risk in risks:
            st.error(risk)
    else:
        st.success("✅ No major risk keywords detected.")

    if suspicious_lines:
        st.subheader("🔎 Lines Containing Suspicious Language")
        for line in suspicious_lines:
            st.code(line, language="markdown")
