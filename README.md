# 🔍 Privacy Policy Lookup

**Privacy Policy Lookup** is a free, AI-powered web tool that scans, summarizes, and flags hidden privacy risks and vague terms in user agreements and privacy policies. It empowers users—especially those who skip reading the fine print—to understand how their data may be used, shared, or misused.

## 🌍 Why It Matters

Most people blindly accept privacy policies without reading them. These documents often contain ambiguous terms or exploitative permissions that put user privacy at risk. **Privacy Policy Lookup** uses natural language processing (NLP) to:

- Detect vague or suspicious language
- Summarize lengthy policies
- Highlight red flags (like hidden data sharing, location/microphone access, etc.)

## 🚀 Key Features

- 🔗 Scan online policies via URL  
- 📄 Upload and analyze PDF, TXT, or pasted raw text  
- 🤖 AI-generated summary using BART transformer  
- ⚠️ Rule-based risk pattern detection  
- 🌐 Web-based app built with open-source tools  

## 🧪 How It Works

1. User provides input (URL, PDF, TXT file, or raw text)
2. Text is extracted and passed through a summarizer
3. Rule-based analyzer flags suspicious patterns
4. Summary and warnings are displayed in a clean dashboard

## 🛠️ Tech Stack

- **Streamlit** — for web interface  
- **Transformers (Hugging Face)** — BART model for summarization  
- **pdfplumber** — PDF text extraction  
- **BeautifulSoup** — HTML parsing from URLs  
- **Python 3.9+**

## 📦 Installation

```bash
git clone https://github.com/Nurumoney/Privacy-Policy-Lookup.git
cd Privacy-Policy-Lookup
pip install -r requirements.txt
streamlit run app.py
```
##Project Structure 📂 

```
```Privacy-Policy-Lookup/
├── app.py                 # Streamlit web app
├── analyzer.py            # Risk detection rules
├── summarizer.py          # AI summarization module
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Streamlit theme config
├── utils/
│   ├── pdf_reader.py      # PDF parser utility
│   └── url_scraper.py     # Web content extractor
└── README.md              # Project overview
