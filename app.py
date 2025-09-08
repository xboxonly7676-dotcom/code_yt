import os
import json
import subprocess
import tempfile
import uuid
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn

# ----------------------------
# Job queue (in memory)
# ----------------------------
JOB_STATUS = {}

# ----------------------------
# Request model
# ----------------------------
class RenderRequest(BaseModel):
    payload: list  # list of {text, audio_url, image_url}

# ----------------------------
# App
# ----------------------------
app = FastAPI()

def run_renderer(job_id: str, payload: list):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
            f.write(json.dumps(payload).encode("utf-8"))
            f.flush()
            file_path = f.name

        cmd = ["python", "render_with_ffmpeg.py", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse signed URL from stdout
        url = None
        for line in result.stdout.splitlines():
            if "Download URL:" in line:
                url = line.split("Download URL:")[-1].strip()

        if url:
            JOB_STATUS[job_id] = {"status": "completed", "url": url}
        else:
            JOB_STATUS[job_id] = {"status": "failed", "error": result.stderr}

    except Exception as e:
        JOB_STATUS[job_id] = {"status": "failed", "error": str(e)}

@app.post("/render")
async def render_video(req: RenderRequest, background_tasks: BackgroundTasks):
    job_id = uuid.uuid4().hex
    JOB_STATUS[job_id] = {"status": "queued"}
    background_tasks.add_task(run_renderer, job_id, req.payload)
    return {"job_id": job_id, "status": "queued"}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    return JOB_STATUS.get(job_id, {"status": "not_found"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
