import json
from pathlib import Path

from app.core.model_repair import needs_sdxl_config_repair, repair_sdxl_onnx_configs


def test_needs_sdxl_config_repair_detects_legacy_onnx_sdxl(tmp_path: Path):
    model_dir = tmp_path / "model"
    (model_dir / "unet").mkdir(parents=True)
    (model_dir / "model_index.json").write_text(
        json.dumps({"_class_name": "ORTStableDiffusionXLPipeline", "unet": ["diffusers", "OnnxRuntimeModel"]}),
        encoding="utf-8",
    )

    assert needs_sdxl_config_repair(model_dir)


def test_repair_sdxl_onnx_configs_copies_component_configs(tmp_path: Path):
    model_dir = tmp_path / "model"
    source_dir = tmp_path / "source"
    for target in ["unet", "vae_decoder", "vae_encoder", "text_encoder", "text_encoder_2"]:
        (model_dir / target).mkdir(parents=True)
    for source in ["unet", "vae", "text_encoder", "text_encoder_2"]:
        (source_dir / source).mkdir(parents=True)
        (source_dir / source / "config.json").write_text(f'{{"source":"{source}"}}', encoding="utf-8")

    repair_sdxl_onnx_configs(model_dir, source_dir=source_dir)

    assert (model_dir / "unet" / "config.json").read_text(encoding="utf-8") == '{"source":"unet"}'
    assert (model_dir / "vae_decoder" / "config.json").read_text(encoding="utf-8") == '{"source":"vae"}'
    assert (model_dir / "vae_encoder" / "config.json").read_text(encoding="utf-8") == '{"source":"vae"}'
