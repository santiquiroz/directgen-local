from app.core.runtime import RuntimeReport, choose_execution_provider, module_available, summarize_runtime


def test_choose_execution_provider_prefers_directml():
    assert choose_execution_provider(["CPUExecutionProvider", "DmlExecutionProvider"]) == "DmlExecutionProvider"


def test_choose_execution_provider_falls_back_to_cpu():
    assert choose_execution_provider(["CPUExecutionProvider"]) == "CPUExecutionProvider"


def test_summarize_runtime_marks_directml_ready():
    report = RuntimeReport(
        onnxruntime_available=True,
        providers=["DmlExecutionProvider", "CPUExecutionProvider"],
        selected_provider="DmlExecutionProvider",
        torch_directml_available=False,
        optimum_available=True,
        errors=[],
    )

    summary = summarize_runtime(report)

    assert summary["directml_ready"] is True
    assert summary["image_generation_ready"] is True


def test_summarize_runtime_marks_torch_directml_ready_without_onnx_provider():
    report = RuntimeReport(
        onnxruntime_available=False,
        providers=[],
        selected_provider=None,
        torch_directml_available=True,
        optimum_available=False,
        errors=[],
    )

    summary = summarize_runtime(report)

    assert summary["directml_ready"] is True
    assert summary["image_generation_ready"] is True


def test_module_available_returns_false_for_missing_nested_module():
    assert module_available("package_that_does_not_exist.submodule") is False
