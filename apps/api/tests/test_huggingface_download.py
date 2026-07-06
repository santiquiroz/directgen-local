from app.core.huggingface import snapshot_allow_patterns


def test_snapshot_allow_patterns_keep_torch_directml_download_small():
    patterns = snapshot_allow_patterns("torch-directml")

    assert patterns is not None
    assert "unet/diffusion_pytorch_model.safetensors" in patterns
    assert "vae/diffusion_pytorch_model.safetensors" in patterns
    assert "*.ckpt" not in patterns


def test_snapshot_allow_patterns_leave_onnx_models_unfiltered():
    assert snapshot_allow_patterns("onnx-directml") is None
