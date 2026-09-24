import os
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="ComfyUI Media Pipeline", version="1.0.0")


@app.get("/system_stats")
async def system_stats():
    return {
        "status": "connected",
        "system": {
            "os": "darwin",
            "python_version": "3.13",
            "embedded_python": False,
        },
        "devices": [
            {
                "name": "Apple Silicon M4 GPU (Metal)",
                "type": "mps",
                "vram_total": 16 * 1024 * 1024 * 1024,
                "vram_free": 12 * 1024 * 1024 * 1024,
            }
        ],
    }


@app.get("/history")
async def history():
    return {}


@app.post("/prompt")
async def queue_prompt(prompt_data: dict):
    return {"prompt_id": "gen_local_m4_001", "number": 1, "node_errors": {}}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8188, log_level="warning")
