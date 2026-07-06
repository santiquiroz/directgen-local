from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.core.catalog import TaskType


@dataclass(frozen=True)
class GenerationRequest:
    model_id: str
    task: TaskType
    prompt: str
    negative_prompt: str
    width: int
    height: int
    steps: int
    guidance_scale: float
    seed: int | None


@dataclass
class GenerationJob:
    id: str
    request: GenerationRequest
    status: str
    output_path: Path
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "request": {
                "model_id": self.request.model_id,
                "task": self.request.task.value,
                "prompt": self.request.prompt,
                "negative_prompt": self.request.negative_prompt,
                "width": self.request.width,
                "height": self.request.height,
                "steps": self.request.steps,
                "guidance_scale": self.request.guidance_scale,
                "seed": self.request.seed,
            },
            "status": self.status,
            "output_path": str(self.output_path),
            "output_url": f"/outputs/{self.output_path.name}",
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "error": self.error,
        }


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, GenerationJob] = {}
        self._lock = Lock()

    def add(self, job: GenerationJob) -> None:
        with self._lock:
            self._jobs[job.id] = job

    def get(self, job_id: str) -> GenerationJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def list(self) -> list[GenerationJob]:
        with self._lock:
            return sorted(self._jobs.values(), key=lambda job: job.created_at, reverse=True)

    def update(self, job_id: str, *, status: str, error: str | None = None) -> GenerationJob | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            job.status = status
            job.error = error
            job.updated_at = datetime.now(UTC)
            return job


def create_generation_job(
    *,
    store: JobStore,
    model_id: str,
    task: TaskType,
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    steps: int,
    guidance_scale: float,
    seed: int | None,
    output_dir: Path,
) -> GenerationJob:
    if not prompt.strip():
        raise ValueError("prompt is required")
    if width < 256 or height < 256:
        raise ValueError("width and height must be at least 256")
    if steps < 1:
        raise ValueError("steps must be greater than zero")

    request = GenerationRequest(
        model_id=model_id.strip(),
        task=task,
        prompt=prompt.strip(),
        negative_prompt=negative_prompt.strip(),
        width=width,
        height=height,
        steps=steps,
        guidance_scale=guidance_scale,
        seed=seed,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "mp4" if task == TaskType.IMAGE_TO_VIDEO else "png"
    job = GenerationJob(
        id=uuid4().hex,
        request=request,
        status="pending",
        output_path=output_dir / f"{uuid4().hex}.{suffix}",
    )
    store.add(job)
    return job
