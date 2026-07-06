from pathlib import Path

from app.core.install_jobs import InstallJobStore, create_install_job, run_install_job
from app.core.model_store import ModelStore


def test_create_install_job_returns_pending_job():
    store = InstallJobStore()

    job = create_install_job(
        store=store,
        repo_id="softwareweaver/stable-diffusion-xl-base-1.0-Olive-Onnx",
        task="text-to-image",
        runtime="onnx-directml",
    )

    assert job.status == "pending"
    assert store.get(job.id).repo_id == "softwareweaver/stable-diffusion-xl-base-1.0-Olive-Onnx"


def test_run_install_job_registers_downloaded_model(tmp_path: Path):
    jobs = InstallJobStore()
    models = ModelStore(tmp_path / "models.json")
    job = create_install_job(
        store=jobs,
        repo_id="softwareweaver/stable-diffusion-xl-base-1.0-Olive-Onnx",
        task="text-to-image",
        runtime="onnx-directml",
    )

    run_install_job(
        job=job,
        jobs=jobs,
        models=models,
        models_dir=tmp_path / "models",
        downloader=lambda *, repo_id, models_dir, runtime: models_dir / repo_id.replace("/", "__"),
    )

    finished = jobs.get(job.id)
    installed = models.list()

    assert finished.status == "succeeded"
    assert finished.model_id == installed[0].id
    assert installed[0].repo_id == "softwareweaver/stable-diffusion-xl-base-1.0-Olive-Onnx"
