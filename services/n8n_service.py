import os
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="n8n Workflow Automation Engine", version="1.0.0")


@app.get("/healthz")
async def healthz():
    return {
        "status": "connected",
        "engine": "n8n Automation Engine",
        "active_workflows": 4,
        "features": ["YouTube Scheduled Uploads", "Daily Auto-Rhyme Creator", "Asset Sync"],
    }


@app.get("/rest/workflows")
async def list_workflows():
    return {
        "data": [
            {"id": "wf_yt_upload", "name": "YouTube Auto-Publisher", "active": True},
            {"id": "wf_batch_rhymes", "name": "Daily Batch Generator", "active": True},
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5678, log_level="warning")
