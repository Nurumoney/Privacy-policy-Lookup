import streamlit as st
import PyPDF2
import requests
from bs4 import BeautifulSoup
import tempfile

# --- CONFIG ---
TTS_API_URL = "https://privacy-policy-lookup.onrender.com/speak"  

# --- PAGE SETUP ---
st.set_page_config(page_title="Privacy Policy Lookup", layout="wide")
st.title("🔍 Privacy Policy Lookup")

# --- TEXT EXTRACTORS ---
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    return ''.join([page.extract_text() or "" for page in reader.pages])

def extract_text_from_url(url):
    try:
        soup = BeautifulSoup(requests.get(url, timeout=10).text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"❌ Failed to fetch: {e}"

# --- DIAGNOSIS ---
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

# --- REMOTE TTS API CALL ---
def generate_voice(text, lang_code):
    payload = {"text": text, "lang": lang_code}
    try:
        response = requests.post(TTS_API_URL, json=payload)
        if response.status_code == 200:
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_audio.write(response.content)
            temp_audio.close()
            return temp_audio.name, None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return None, str(e)

# --- SIDEBAR INPUT ---
st.sidebar.header("📥 Input Options")
source_option = st.sidebar.radio("Select source:", ["Paste Text", "Upload PDF", "Enter URL"])
raw_text = url = ""
uploaded_file = None

if source_option == "Paste Text":
    raw_text = st.text_area("📋 Paste Privacy Policy Text", height=300)
elif source_option == "Upload PDF":
    uploaded_file = st.file_uploader("📄 Upload a PDF File", type=["pdf"])
elif source_option == "Enter URL":
    url = st.text_input("🌐 Enter Privacy Policy URL")

# --- PROCESSING TRIGGER ---
if st.button("Analyze"):
    if source_option == "Paste Text" and raw_text.strip():
        st.session_state["final_text"] = raw_text.strip()
    elif source_option == "Upload PDF" and uploaded_file:
        st.session_state["final_text"] = extract_text_from_pdf(uploaded_file)
    elif source_option == "Enter URL" and url.strip():
        st.session_state["final_text"] = extract_text_from_url(url.strip())
    else:
        st.warning("⚠️ Please provide input.")

    st.session_state["risks"], st.session_state["suspicious_lines"] = analyze_policy(st.session_state["final_text"])

# --- RESULTS ---
if "final_text" in st.session_state:
    st.subheader("📄 Extracted Policy Text")
    with st.expander("Click to view full text"):
        st.write(st.session_state["final_text"][:5000])

    st.subheader("🧠 AI Diagnosis")
    if st.session_state["risks"]:
        for risk in st.session_state["risks"]:
            st.error(risk)
    else:
        st.success("✅ No major red flags detected.")

    st.subheader("🧾 Suspicious Lines")
    for line in st.session_state["suspicious_lines"]:
        st.code(line)

    st.subheader("🎧 Voice Summary")
    lang_choice = st.selectbox("Choose Language", ["None", "Hausa", "Yoruba"])
    lang_map = {"Hausa": "ha", "Yoruba": "yo"}

    if lang_choice in lang_map:
        summary_text = (
            "This privacy policy may contain serious risks."
            if st.session_state["risks"]
            else "This policy appears safe with no critical issues."
        )
        audio_file, error = generate_voice(summary_text, lang_map[lang_choice])
        if audio_file:
            st.audio(audio_file)
        else:
            st.error(f"Voice generation failed: {error}")
