from app.main import GenerateRequest


def test_generate_request_defaults_to_directml_safe_resolution():
    request = GenerateRequest(model_id="local-sdxl", prompt="apple pie")

    assert request.width == 768
    assert request.height == 768
