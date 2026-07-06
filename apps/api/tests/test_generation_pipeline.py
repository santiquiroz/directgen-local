import json
from pathlib import Path

from app.core.generation import choose_pipeline_class_name


def test_choose_pipeline_class_name_uses_sdxl_specific_pipeline(tmp_path: Path):
    (tmp_path / "model_index.json").write_text(
        json.dumps({"_class_name": "ORTStableDiffusionXLPipeline"}),
        encoding="utf-8",
    )

    assert choose_pipeline_class_name(tmp_path) == "ORTStableDiffusionXLPipeline"


def test_choose_pipeline_class_name_falls_back_to_generic_pipeline(tmp_path: Path):
    assert choose_pipeline_class_name(tmp_path) == "ORTDiffusionPipeline"
