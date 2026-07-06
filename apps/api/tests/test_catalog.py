from app.core.catalog import TaskType, get_curated_models, validate_repo_id


def test_curated_models_include_directml_ready_image_presets():
    models = get_curated_models()

    directml_ready = [model for model in models if model.directml == "ready"]

    assert directml_ready
    assert any(model.task == TaskType.TEXT_TO_IMAGE for model in directml_ready)
    assert all(model.repo_id for model in models)


def test_curated_models_recommend_torch_directml_stable_diffusion_first():
    model = get_curated_models()[0]

    assert model.repo_id == "CompVis/stable-diffusion-v1-4"
    assert model.runtime == "torch-directml"
    assert model.directml == "ready"


def test_validate_repo_id_accepts_normal_hugging_face_ids():
    assert validate_repo_id("stabilityai/stable-diffusion-xl-base-1.0")
    assert validate_repo_id("softwareweaver/stable-diffusion-xl-base-1.0-Olive-Onnx")


def test_validate_repo_id_rejects_paths_and_urls():
    assert not validate_repo_id("../models/sd")
    assert not validate_repo_id("https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0")
    assert not validate_repo_id("owner/model/name")
