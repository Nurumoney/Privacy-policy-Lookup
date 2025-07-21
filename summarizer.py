from transformers import pipeline

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def generate_summary(text, max_length=300):
    if len(text) < 50:
        return "Text too short to summarize."
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summary = ""
    for chunk in chunks:
        result = summarizer(chunk, max_length=max_length, min_length=50, do_sample=False)
        summary += result[0]['summary_text'] + " "
    return summary.strip()
