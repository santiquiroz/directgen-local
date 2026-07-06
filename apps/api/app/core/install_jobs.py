from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.core.huggingface import download_model_snapshot
from app.core.model_repair import repair_model_if_needed
from app.core.model_store import ModelStore


@dataclass
class InstallJob:
    id: str
    repo_id: str
    task: str
    runtime: str
    status: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    model_id: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "repo_id": self.repo_id,
            "task": self.task,
            "runtime": self.runtime,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "model_id": self.model_id,
            "error": self.error,
        }


class InstallJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, InstallJob] = {}
        self._lock = Lock()

    def add(self, job: InstallJob) -> None:
        with self._lock:
            self._jobs[job.id] = job

    def get(self, job_id: str) -> InstallJob:
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(job_id)
            return self._jobs[job_id]

    def list(self) -> list[InstallJob]:
        with self._lock:
            return sorted(self._jobs.values(), key=lambda job: job.created_at, reverse=True)

    def update(
        self,
        job_id: str,
        *,
        status: str,
        model_id: str | None = None,
        error: str | None = None,
    ) -> InstallJob:
        with self._lock:
            job = self._jobs[job_id]
            job.status = status
            job.model_id = model_id
            job.error = error
            job.updated_at = datetime.now(UTC)
            return job


def create_install_job(*, store: InstallJobStore, repo_id: str, task: str, runtime: str) -> InstallJob:
    job = InstallJob(
        id=uuid4().hex,
        repo_id=repo_id.strip(),
        task=task,
        runtime=runtime,
        status="pending",
    )
    store.add(job)
    return job


def run_install_job(
    *,
    job: InstallJob,
    jobs: InstallJobStore,
    models: ModelStore,
    models_dir: Path,
    downloader: Callable[..., Path] = download_model_snapshot,
) -> None:
    jobs.update(job.id, status="running")
    try:
        local_path = downloader(repo_id=job.repo_id, models_dir=models_dir, runtime=job.runtime)
        repair_model_if_needed(local_path)
        model = models.register(repo_id=job.repo_id, local_path=local_path, task=job.task, runtime=job.runtime)
        jobs.update(job.id, status="succeeded", model_id=model.id)
    except Exception as exc:
        jobs.update(job.id, status="failed", error=str(exc))
