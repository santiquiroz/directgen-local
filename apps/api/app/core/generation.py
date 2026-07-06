from __future__ import annotations

import json
from pathlib import Path

from app.core.catalog import TaskType
from app.core.jobs import GenerationJob, JobStore
from app.core.model_store import ModelStore
from app.core.runtime import detect_runtime


def run_generation_job(*, job: GenerationJob, jobs: JobStore, models: ModelStore) -> None:
    jobs.update(job.id, status="running")
    try:
        installed = models.get(job.request.model_id)
        if job.request.task == TaskType.IMAGE_TO_VIDEO:
            raise RuntimeError(
                "Video generation is experimental on DirectML. The current MVP supports image generation via ONNX Runtime first."
            )
        if installed.runtime != "onnx-directml":
            raise RuntimeError(f"Unsupported runtime for this MVP: {installed.runtime}")

        generate_image_onnx_directml(job=job, model_path=Path(installed.local_path))
        jobs.update(job.id, status="succeeded")
    except Exception as exc:
        jobs.update(job.id, status="failed", error=str(exc))


def generate_image_onnx_directml(*, job: GenerationJob, model_path: Path) -> None:
    report = detect_runtime()
    if not report.onnxruntime_available:
        raise RuntimeError("onnxruntime is not installed. Run scripts/setup-api.ps1 first.")
    if report.selected_provider != "DmlExecutionProvider":
        raise RuntimeError("DmlExecutionProvider is not available. Check GPU drivers and onnxruntime-directml.")
    if not report.optimum_available:
        raise RuntimeError("optimum[onnxruntime] is not installed. Run scripts/setup-api.ps1 first.")

    if job.request.seed is not None:
        import numpy as np

        np.random.seed(job.request.seed)

    pipeline_class = load_pipeline_class(model_path)
    pipe = pipeline_class.from_pretrained(str(model_path), provider="DmlExecutionProvider")
    result = pipe(
        prompt=job.request.prompt,
        negative_prompt=job.request.negative_prompt or None,
        width=job.request.width,
        height=job.request.height,
        num_inference_steps=job.request.steps,
        guidance_scale=job.request.guidance_scale,
    )
    image = result.images[0]
    job.output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(job.output_path)


def choose_pipeline_class_name(model_path: Path) -> str:
    model_index = model_path / "model_index.json"
    if not model_index.exists():
        return "ORTDiffusionPipeline"
    data = json.loads(model_index.read_text(encoding="utf-8"))
    if data.get("_class_name") == "ORTStableDiffusionXLPipeline":
        return "ORTStableDiffusionXLPipeline"
    return "ORTDiffusionPipeline"


def load_pipeline_class(model_path: Path):
    from optimum import onnxruntime

    return getattr(onnxruntime, choose_pipeline_class_name(model_path))
