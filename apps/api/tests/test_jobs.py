from pathlib import Path

from app.core.jobs import JobStore, create_generation_job
from app.core.catalog import TaskType


def test_create_generation_job_stores_pending_job(tmp_path: Path):
    store = JobStore()

    job = create_generation_job(
        store=store,
        model_id="local-sdxl",
        task=TaskType.TEXT_TO_IMAGE,
        prompt="cinematic photo of a glass city",
        negative_prompt="blurry",
        width=1024,
        height=1024,
        steps=20,
        guidance_scale=7.5,
        seed=42,
        output_dir=tmp_path,
    )

    stored = store.get(job.id)

    assert stored is not None
    assert stored.status == "pending"
    assert stored.request.prompt == "cinematic photo of a glass city"
    assert stored.output_path.parent == tmp_path


def test_create_generation_job_rejects_empty_prompt(tmp_path: Path):
    store = JobStore()

    try:
        create_generation_job(
            store=store,
            model_id="local-sdxl",
            task=TaskType.TEXT_TO_IMAGE,
            prompt=" ",
            negative_prompt="",
            width=1024,
            height=1024,
            steps=20,
            guidance_scale=7.5,
            seed=None,
            output_dir=tmp_path,
        )
    except ValueError as exc:
        assert "prompt" in str(exc).lower()
    else:
        raise AssertionError("Expected empty prompt to be rejected")
