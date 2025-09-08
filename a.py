from fastapi import FastAPI, BackgroundTasks
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/render")
def render_video(payload: dict, background_tasks: BackgroundTasks):
    # TODO: call your render_with_ffmpeg.py logic here in background
    return {"job_id": "123"}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    # TODO: check job status and return download URL if complete
    return {"status": "pending", "job_id": job_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
