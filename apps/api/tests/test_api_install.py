from fastapi import BackgroundTasks

from app import main


def test_install_endpoint_returns_job_without_waiting_for_download(monkeypatch):
    monkeypatch.setattr(main, "run_install_job", lambda **_: None)

    body = main.install_model(
        main.InstallModelRequest(
            repo_id="softwareweaver/stable-diffusion-xl-base-1.0-Olive-Onnx",
            task=main.TaskType.TEXT_TO_IMAGE,
            runtime="onnx-directml",
        ),
        BackgroundTasks(),
    )

    assert body["status"] == "pending"
    assert body["repo_id"] == "softwareweaver/stable-diffusion-xl-base-1.0-Olive-Onnx"
