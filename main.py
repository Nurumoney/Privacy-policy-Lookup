from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from TTS.api import TTS
import uuid
import os

app = FastAPI()

# Load Coqui TTS model (adjust model name if needed)
tts_model = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v1", progress_bar=False)

# Input schema
class TTSRequest(BaseModel):
    text: str
    lang: str  # e.g., "ha", "yo", or "en"

@app.post("/speak")
def speak(data: TTSRequest):
    try:
        os.makedirs("audio", exist_ok=True)
        filename = f"{uuid.uuid4().hex}.wav"
        filepath = os.path.join("audio", filename)

        # You can add voice style logic here if needed
        tts_model.tts_to_file(text=data.text, file_path=filepath)

        return FileResponse(filepath, media_type="audio/wav")

    except Exception as e:
        return {"error": str(e)}
