from __future__ import annotations

import json
import shutil
from pathlib import Path


SDXL_BASE_REPO = "stabilityai/stable-diffusion-xl-base-1.0"


def needs_sdxl_config_repair(model_dir: Path) -> bool:
    model_index_path = model_dir / "model_index.json"
    if not model_index_path.exists():
        return False

    model_index = json.loads(model_index_path.read_text(encoding="utf-8"))
    return (
        model_index.get("_class_name") == "ORTStableDiffusionXLPipeline"
        and model_index.get("unet") == ["diffusers", "OnnxRuntimeModel"]
        and not (model_dir / "unet" / "config.json").exists()
    )


def repair_sdxl_onnx_configs(model_dir: Path, *, source_dir: Path | None = None) -> None:
    source = source_dir or _download_sdxl_base_configs()
    copies = {
        "unet": "unet",
        "vae_decoder": "vae",
        "vae_encoder": "vae",
        "text_encoder": "text_encoder",
        "text_encoder_2": "text_encoder_2",
    }
    for target, source_name in copies.items():
        target_config = model_dir / target / "config.json"
        if target_config.exists():
            continue
        shutil.copyfile(source / source_name / "config.json", target_config)


def repair_model_if_needed(model_dir: Path) -> None:
    if needs_sdxl_config_repair(model_dir):
        repair_sdxl_onnx_configs(model_dir)


def _download_sdxl_base_configs() -> Path:
    from huggingface_hub import hf_hub_download

    first_path: Path | None = None
    for folder in ["unet", "vae", "text_encoder", "text_encoder_2"]:
        path = Path(hf_hub_download(SDXL_BASE_REPO, f"{folder}/config.json"))
        first_path = first_path or path
    if first_path is None:
        raise RuntimeError("Could not download SDXL base configs")
    return first_path.parents[1]
