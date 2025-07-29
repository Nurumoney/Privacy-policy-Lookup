import streamlit as st
import requests
from bs4 import BeautifulSoup
import PyPDF2
from gtts import gTTS
import tempfile

# Setup session state
if "final_text" not in st.session_state:
    st.session_state["final_text"] = ""
if "risks" not in st.session_state:
    st.session_state["risks"] = []
if "suspicious_lines" not in st.session_state:
    st.session_state["suspicious_lines"] = []

# --- Streamlit Config ---
st.set_page_config(page_title="Privacy Policy Lookup", layout="wide")
st.title("🔍 Privacy Policy Lookup")

# --- Functions ---
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
        return f"❌ Failed to fetch: {e}"

def analyze_policy(text):
    lower_text = text.lower()
    risks = []
    suspicious_lines = []

    keywords = [
        "sell your data", "share with third parties", "track your location",
        "store indefinitely", "targeted ads", "use your contacts", "camera access",
        "read your sms", "microphone access", "collect device information"
    ]

    lines = text.split('\n')
    for line in lines:
        for keyword in keywords:
            if keyword in line.lower():
                risks.append(f"⚠️ Found keyword: '{keyword}'")
                suspicious_lines.append(line.strip())
    return risks, suspicious_lines

def generate_voice(text, lang_code):
    try:
        short_text = text[:500]
        tts = gTTS(short_text, lang=lang_code)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name, None
    except Exception as e:
        return None, str(e)

# --- Sidebar Input ---
st.sidebar.header("📥 Input Options")
source_option = st.sidebar.radio("Select input source:", ["Paste Text", "Upload PDF", "Enter URL"])
uploaded_file = None
raw_text = ""
url = ""

if source_option == "Paste Text":
    raw_text = st.text_area("Paste the privacy policy text here:", height=300)

elif source_option == "Upload PDF":
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

elif source_option == "Enter URL":
    url = st.text_input("Enter the URL of the privacy policy")

# --- Trigger Analysis ---
if st.button("Analyze"):
    if source_option == "Paste Text" and raw_text.strip():
        st.session_state["final_text"] = raw_text.strip()
    elif source_option == "Upload PDF" and uploaded_file:
        st.session_state["final_text"] = extract_text_from_pdf(uploaded_file)
    elif source_option == "Enter URL" and url.strip():
        st.session_state["final_text"] = extract_text_from_url(url.strip())

    # Clear previous results
    st.session_state["risks"], st.session_state["suspicious_lines"] = analyze_policy(st.session_state["final_text"])

# --- Display Analysis ---
if st.session_state["final_text"]:
    st.subheader("📄 Extracted Policy Text")
    with st.expander("Click to view raw text"):
        st.write(st.session_state["final_text"][:5000])

    st.subheader("🚨 Risk Detection Results")
    if st.session_state["risks"]:
        for risk in st.session_state["risks"]:
            st.error(risk)
    else:
        st.success("✅ No major risk keywords found.")

    if st.session_state["suspicious_lines"]:
        st.subheader("🔎 Suspicious Lines")
        for line in st.session_state["suspicious_lines"]:
            st.code(line)

    # --- Language & Voice Output ---
    st.subheader("🎧 Voice Summary in Local Language")
    language_choice = st.selectbox("Choose a language", ["None", "Hausa", "Yoruba"], key="lang_audio")
    lang_codes = {"Hausa": "ha", "Yoruba": "yo"}

    if language_choice in lang_codes:
        summary_text = (
            "Warning. This policy may contain harmful terms. "
            if st.session_state["risks"] else
            "This privacy policy appears safe. No suspicious keywords were found."
        )
        audio_path, err = generate_voice(summary_text, lang_codes[language_choice])
        if audio_path:
            st.audio(audio_path)
        else:
            st.warning(f"❌ Failed to generate audio: {err}")
