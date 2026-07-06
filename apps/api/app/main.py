from __future__ import annotations

from typing import Literal

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.core.catalog import TaskType, get_curated_models, validate_repo_id
from app.core.generation import run_generation_job
from app.core.huggingface import download_model_snapshot, search_hub_models
from app.core.jobs import JobStore, create_generation_job
from app.core.model_store import ModelStore
from app.core.runtime import detect_runtime, summarize_runtime
from app.settings import MODEL_DIR, OUTPUT_DIR, REGISTRY_PATH


app = FastAPI(title="DirectGen Local API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

jobs = JobStore()
models = ModelStore(REGISTRY_PATH)


class InstallModelRequest(BaseModel):
    repo_id: str
    task: TaskType = TaskType.TEXT_TO_IMAGE
    runtime: Literal["onnx-directml", "torch-directml"] = "onnx-directml"


class GenerateRequest(BaseModel):
    model_id: str
    task: TaskType = TaskType.TEXT_TO_IMAGE
    prompt: str = Field(min_length=1)
    negative_prompt: str = ""
    width: int = Field(default=1024, ge=256, le=2048)
    height: int = Field(default=1024, ge=256, le=2048)
    steps: int = Field(default=24, ge=1, le=150)
    guidance_scale: float = Field(default=7.0, ge=0, le=30)
    seed: int | None = None


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/runtime")
def runtime() -> dict[str, object]:
    return summarize_runtime(detect_runtime())


@app.get("/api/models/presets")
def presets() -> list[dict[str, object]]:
    return [model.to_dict() for model in get_curated_models()]


@app.get("/api/models/installed")
def installed_models() -> list[dict[str, str]]:
    return [model.to_dict() for model in models.list()]


@app.get("/api/models/search")
def search_models(query: str = "", task: TaskType = TaskType.TEXT_TO_IMAGE) -> list[dict[str, object]]:
    try:
        return search_hub_models(query=query, task=task.value)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/models/install")
def install_model(request: InstallModelRequest) -> dict[str, str]:
    if not validate_repo_id(request.repo_id):
        raise HTTPException(status_code=400, detail="Invalid Hugging Face repo id")
    try:
        local_path = download_model_snapshot(repo_id=request.repo_id, models_dir=MODEL_DIR)
        model = models.register(
            repo_id=request.repo_id,
            local_path=local_path,
            task=request.task.value,
            runtime=request.runtime,
        )
        return model.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/generate/jobs")
def create_job(request: GenerateRequest, background_tasks: BackgroundTasks) -> dict[str, object]:
    try:
        job = create_generation_job(
            store=jobs,
            model_id=request.model_id,
            task=request.task,
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            steps=request.steps,
            guidance_scale=request.guidance_scale,
            seed=request.seed,
            output_dir=OUTPUT_DIR,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    background_tasks.add_task(run_generation_job, job=job, jobs=jobs, models=models)
    return job.to_dict()


@app.get("/api/generate/jobs")
def list_jobs() -> list[dict[str, object]]:
    return [job.to_dict() for job in jobs.list()]


@app.get("/api/generate/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, object]:
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()
