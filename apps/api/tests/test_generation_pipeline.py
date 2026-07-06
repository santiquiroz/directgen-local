import json
from pathlib import Path

from app.core.catalog import TaskType
from app.core.generation import choose_pipeline_class_name, run_generation_job, safe_error_message
from app.core.jobs import JobStore, create_generation_job
from app.core.model_store import ModelStore


def test_choose_pipeline_class_name_uses_sdxl_specific_pipeline(tmp_path: Path):
    (tmp_path / "model_index.json").write_text(
        json.dumps({"_class_name": "ORTStableDiffusionXLPipeline"}),
        encoding="utf-8",
    )

    assert choose_pipeline_class_name(tmp_path) == "ORTStableDiffusionXLPipeline"


def test_choose_pipeline_class_name_falls_back_to_generic_pipeline(tmp_path: Path):
    assert choose_pipeline_class_name(tmp_path) == "ORTDiffusionPipeline"


def test_safe_error_message_preserves_directml_failures_without_encoding_crash():
    error = UnicodeDecodeError("utf-8", b"DirectML fall\xf3", 14, 15, "invalid continuation byte")

    message = safe_error_message(error)

    assert "utf-8 codec could not decode error details" in message
    assert "Try 768x768" in message


def test_run_generation_job_dispatches_torch_directml_models(tmp_path: Path, monkeypatch):
    calls = []
    models = ModelStore(tmp_path / "registry.json")
    installed = models.register(
        repo_id="CompVis/stable-diffusion-v1-4",
        local_path=tmp_path / "models" / "sd14",
        task=TaskType.TEXT_TO_IMAGE.value,
        runtime="torch-directml",
    )
    jobs = JobStore()
    job = create_generation_job(
        store=jobs,
        model_id=installed.id,
        task=TaskType.TEXT_TO_IMAGE,
        prompt="apple pie",
        negative_prompt="",
        width=512,
        height=512,
        steps=4,
        guidance_scale=7.5,
        seed=None,
        output_dir=tmp_path / "outputs",
    )

    def fake_generate(*, job, model_path):
        calls.append((job.id, model_path))

    monkeypatch.setattr("app.core.generation.generate_image_torch_directml", fake_generate, raising=False)

    run_generation_job(job=job, jobs=jobs, models=models)

    assert jobs.get(job.id).status == "succeeded"
    assert calls == [(job.id, Path(installed.local_path))]
