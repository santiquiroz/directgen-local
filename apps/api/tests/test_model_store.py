from pathlib import Path

from app.core.model_store import ModelStore


def test_model_store_round_trips_installed_model(tmp_path: Path):
    store = ModelStore(tmp_path / "models.json")

    model = store.register(
        repo_id="softwareweaver/stable-diffusion-xl-base-1.0-Olive-Onnx",
        local_path=tmp_path / "sdxl",
        task="text-to-image",
        runtime="onnx-directml",
    )

    reloaded = ModelStore(tmp_path / "models.json")

    assert reloaded.list()[0].id == model.id
    assert reloaded.get(model.id).repo_id == "softwareweaver/stable-diffusion-xl-base-1.0-Olive-Onnx"
