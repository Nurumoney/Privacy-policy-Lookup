import streamlit as st
import requests
from bs4 import BeautifulSoup
import PyPDF2
from gtts import gTTS
import tempfile

# Session setup
if "final_text" not in st.session_state:
    st.session_state["final_text"] = ""
if "risks" not in st.session_state:
    st.session_state["risks"] = []
if "suspicious_lines" not in st.session_state:
    st.session_state["suspicious_lines"] = []

# Page config
st.set_page_config(page_title="Privacy Policy Checker", layout="wide")
st.title("🔍 Privacy Policy Lookup")

# Extractors
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    return ''.join([page.extract_text() or "" for page in reader.pages])

def extract_text_from_url(url):
    try:
        soup = BeautifulSoup(requests.get(url, timeout=10).text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"❌ Failed to fetch: {e}"

# Analyzer
def analyze_policy(text):
    text = text.lower()
    risks = []
    suspicious_lines = []

    rules = {
        "📍 Location Tracking": ["gps", "track location", "access location"],
        "📞 Contact Access": ["contact list", "phonebook", "access contacts"],
        "📩 SMS Surveillance": ["read sms", "sms inbox", "message content"],
        "📡 Device Monitoring": ["microphone", "camera", "call logs"],
        "🔗 Data Sharing": ["third parties", "affiliates", "advertisers", "sell your data"]
    }

    for line in text.split('\n'):
        for risk_label, terms in rules.items():
            for term in terms:
                if term in line:
                    risks.append(f"{risk_label} – found: '{term}'")
                    suspicious_lines.append(line.strip())
                    break
    return list(set(risks)), list(set(suspicious_lines))

# TTS function
def generate_voice(text, lang_code):
    translations = {
        "ha": "Gargaɗi! Wannan manhaja na iya tattara bayanan ka ba tare da izini ba.",
        "yo": "Ikilọ! Ìlànà ìpamọ yìí lè kó alaye rẹ lọ lai fi to ọ létí."
    }
    short_text = translations.get(lang_code, text[:500])
    try:
        tts = gTTS(short_text, lang="en")  # still English voice
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name, None
    except Exception as e:
        return None, str(e)

# Sidebar
st.sidebar.header("📥 Input Options")
source_option = st.sidebar.radio("Select source:", ["Paste Text", "Upload PDF", "Enter URL"])
uploaded_file = raw_text = url = ""

if source_option == "Paste Text":
    raw_text = st.text_area("📋 Paste text here:", height=300)

elif source_option == "Upload PDF":
    uploaded_file = st.file_uploader("📄 Upload a PDF", type=["pdf"])

elif source_option == "Enter URL":
    url = st.text_input("🌐 Enter Privacy Policy URL")

if st.button("Analyze"):
    if source_option == "Paste Text" and raw_text.strip():
        st.session_state["final_text"] = raw_text.strip()
    elif source_option == "Upload PDF" and uploaded_file:
        st.session_state["final_text"] = extract_text_from_pdf(uploaded_file)
    elif source_option == "Enter URL" and url.strip():
        st.session_state["final_text"] = extract_text_from_url(url.strip())
    else:
        st.warning("Please provide input.")

    # Analyze
    st.session_state["risks"], st.session_state["suspicious_lines"] = analyze_policy(st.session_state["final_text"])

# Display results
if st.session_state["final_text"]:
    st.subheader("📄 Extracted Policy Text")
    with st.expander("Click to view full text"):
        st.write(st.session_state["final_text"][:5000])

    st.subheader("🧠 Risk Diagnosis")
    if st.session_state["risks"]:
        for risk in st.session_state["risks"]:
            st.error(risk)
    else:
        st.success("✅ No major red flags found.")

    st.subheader("🔎 Suspicious Lines")
    for line in st.session_state["suspicious_lines"]:
        st.code(line)

    st.subheader("🎧 Voice Summary (Local Language)")
    lang_choice = st.selectbox("Choose summary language", ["None", "Hausa", "Yoruba"], key="voice_lang")
    lang_map = {"Hausa": "ha", "Yoruba": "yo"}

    if lang_choice in lang_map:
        summary = (
            "This policy may contain serious privacy risks."
            if st.session_state["risks"]
            else "This policy appears to be safe with no risky flags."
        )
        audio_file, err = generate_voice(summary, lang_map[lang_choice])
        if audio_file:
            st.audio(audio_file)
        else:
            st.warning(f"❌ Voice error: {err}")
