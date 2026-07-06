from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from enum import StrEnum


class TaskType(StrEnum):
    TEXT_TO_IMAGE = "text-to-image"
    IMAGE_TO_IMAGE = "image-to-image"
    INPAINTING = "inpainting"
    IMAGE_TO_VIDEO = "image-to-video"


@dataclass(frozen=True)
class ModelPreset:
    id: str
    name: str
    repo_id: str
    task: TaskType
    family: str
    directml: str
    notes: str
    recommended_vram_gb: int

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["task"] = self.task.value
        return data


_REPO_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}/[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


def validate_repo_id(repo_id: str) -> bool:
    return bool(_REPO_ID_RE.fullmatch(repo_id.strip()))


def get_curated_models() -> list[ModelPreset]:
    return [
        ModelPreset(
            id="sdxl-olive-onnx",
            name="Stable Diffusion XL ONNX Olive",
            repo_id="softwareweaver/stable-diffusion-xl-base-1.0-Olive-Onnx",
            task=TaskType.TEXT_TO_IMAGE,
            family="Stable Diffusion XL",
            directml="ready",
            notes="ONNX/Olive preset for DirectML-first image generation.",
            recommended_vram_gb=12,
        ),
        ModelPreset(
            id="sd15-onnx",
            name="Stable Diffusion 1.5 ONNX",
            repo_id="runwayml/stable-diffusion-v1-5",
            task=TaskType.TEXT_TO_IMAGE,
            family="Stable Diffusion 1.x",
            directml="convert",
            notes="Popular baseline; install as Diffusers model, then export/optimize to ONNX.",
            recommended_vram_gb=8,
        ),
        ModelPreset(
            id="sdxl-base",
            name="Stable Diffusion XL Base",
            repo_id="stabilityai/stable-diffusion-xl-base-1.0",
            task=TaskType.TEXT_TO_IMAGE,
            family="Stable Diffusion XL",
            directml="convert",
            notes="High quality base model; best used after ONNX export and Olive optimization.",
            recommended_vram_gb=16,
        ),
        ModelPreset(
            id="svd-xt",
            name="Stable Video Diffusion XT",
            repo_id="stabilityai/stable-video-diffusion-img2vid-xt",
            task=TaskType.IMAGE_TO_VIDEO,
            family="Stable Video Diffusion",
            directml="experimental",
            notes="Video support is experimental on DirectML; expect torch-directml constraints.",
            recommended_vram_gb=16,
        ),
    ]
