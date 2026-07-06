from __future__ import annotations

import importlib.util
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeReport:
    onnxruntime_available: bool
    providers: list[str]
    selected_provider: str | None
    torch_directml_available: bool
    optimum_available: bool
    errors: list[str]


def choose_execution_provider(providers: list[str]) -> str | None:
    if "DmlExecutionProvider" in providers:
        return "DmlExecutionProvider"
    if "CPUExecutionProvider" in providers:
        return "CPUExecutionProvider"
    return providers[0] if providers else None


def module_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False


def detect_runtime() -> RuntimeReport:
    errors: list[str] = []
    providers: list[str] = []
    onnxruntime_available = module_available("onnxruntime")

    if onnxruntime_available:
        try:
            import onnxruntime as ort

            providers = list(ort.get_available_providers())
        except Exception as exc:  # pragma: no cover - hardware/runtime dependent
            errors.append(f"onnxruntime provider detection failed: {exc}")
    else:
        errors.append("onnxruntime is not installed")

    torch_directml_available = module_available("torch_directml")
    optimum_available = module_available("optimum.onnxruntime")

    if onnxruntime_available and "DmlExecutionProvider" not in providers and not torch_directml_available:
        errors.append("DmlExecutionProvider is not available")
    if not optimum_available and not torch_directml_available:
        errors.append("optimum[onnxruntime] or torch-directml is not installed")

    return RuntimeReport(
        onnxruntime_available=onnxruntime_available,
        providers=providers,
        selected_provider=choose_execution_provider(providers),
        torch_directml_available=torch_directml_available,
        optimum_available=optimum_available,
        errors=errors,
    )


def summarize_runtime(report: RuntimeReport) -> dict[str, object]:
    onnx_directml_ready = report.selected_provider == "DmlExecutionProvider"
    directml_ready = onnx_directml_ready or report.torch_directml_available
    return {
        "onnxruntime_available": report.onnxruntime_available,
        "providers": report.providers,
        "selected_provider": report.selected_provider,
        "torch_directml_available": report.torch_directml_available,
        "optimum_available": report.optimum_available,
        "directml_ready": directml_ready,
        "image_generation_ready": onnx_directml_ready and report.optimum_available or report.torch_directml_available,
        "video_generation_ready": report.torch_directml_available,
        "errors": report.errors,
    }
