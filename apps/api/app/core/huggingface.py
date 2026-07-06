from __future__ import annotations

from pathlib import Path

from app.core.catalog import validate_repo_id


def search_hub_models(*, query: str, task: str, limit: int = 12) -> list[dict[str, object]]:
    try:
        from huggingface_hub import HfApi
    except ImportError as exc:
        raise RuntimeError("huggingface_hub is not installed") from exc

    api = HfApi()
    models = api.list_models(filter=task, search=query or None, sort="downloads", direction=-1, limit=limit)
    return [
        {
            "repo_id": model.id,
            "downloads": getattr(model, "downloads", None),
            "likes": getattr(model, "likes", None),
            "tags": getattr(model, "tags", []),
            "pipeline_tag": getattr(model, "pipeline_tag", None),
            "last_modified": str(getattr(model, "last_modified", "")),
        }
        for model in models
    ]


def snapshot_allow_patterns(runtime: str) -> list[str] | None:
    if runtime != "torch-directml":
        return None
    return [
        "model_index.json",
        "README.md",
        "feature_extractor/*",
        "scheduler/scheduler_config.json",
        "text_encoder/config.json",
        "text_encoder/model.safetensors",
        "tokenizer/*",
        "unet/config.json",
        "unet/diffusion_pytorch_model.safetensors",
        "vae/config.json",
        "vae/diffusion_pytorch_model.safetensors",
    ]


def download_model_snapshot(*, repo_id: str, models_dir: Path, runtime: str = "onnx-directml") -> Path:
    if not validate_repo_id(repo_id):
        raise ValueError("Invalid Hugging Face repo id")

    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("huggingface_hub is not installed") from exc

    target_dir = models_dir / repo_id.replace("/", "__")
    target_dir.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=repo_id, local_dir=target_dir, allow_patterns=snapshot_allow_patterns(runtime))
    return target_dir
