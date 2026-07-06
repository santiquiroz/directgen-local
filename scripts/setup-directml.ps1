$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (!(Test-Path $Python)) {
    throw "Python venv not found. Run scripts\setup-api.ps1 first."
}

function Invoke-Pip {
    & $Python -m pip @args
    if ($LASTEXITCODE -ne 0) {
        throw "pip command failed: $($args -join ' ')"
    }
}

Invoke-Pip install --upgrade pip
Invoke-Pip install --prefer-binary -r (Join-Path $Root "apps\api\requirements-directml.txt")
Invoke-Pip uninstall -y onnxruntime
Invoke-Pip install --prefer-binary --force-reinstall "numpy>=1.26,<2.3"
Invoke-Pip install --prefer-binary --force-reinstall --no-deps "onnxruntime-directml>=1.19,<2"

Write-Host "DirectML dependencies installed. Run scripts\check-runtime.ps1 to verify DmlExecutionProvider."
