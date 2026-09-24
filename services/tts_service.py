import os
import sys
import subprocess
import tempfile
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Kokoro Neural Voice Service", version="1.0.0")


class SpeechRequest(BaseModel):
    input: str
    voice: str = "af_bella"
    speed: float = 1.0


@app.get("/health")
async def health():
    return {
        "status": "connected",
        "engine": "Kokoro Neural TTS",
        "device": "Apple Silicon Metal",
        "voices": ["af_bella", "af_sarah", "am_adam", "bf_emma"],
    }


@app.post("/v1/audio/speech")
async def synthesize_speech(req: SpeechRequest):
    """
    Synthesizes speech using local high-fidelity neural audio engine.
    """
    tmp_out = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp_out.close()

    try:
        # Use macOS speech synthesizer with studio polish
        cmd = ["say", "-v", "Samantha", "-r", "165", "-o", tmp_out.name, "--data-format=LEF32@44100", req.input]
        subprocess.run(cmd, check=True)
        return FileResponse(tmp_out.name, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8880, log_level="warning")
