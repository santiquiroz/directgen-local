$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (!(Test-Path $Python)) {
    throw "Python venv not found. Run scripts\setup-api.ps1 first."
}

$env:PYTHONPATH = Join-Path $Root "apps\api"
& $Python -c "from app.core.runtime import detect_runtime, summarize_runtime; import json; print(json.dumps(summarize_runtime(detect_runtime()), indent=2))"
