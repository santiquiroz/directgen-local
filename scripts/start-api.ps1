$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (!(Test-Path $Python)) {
    throw "Python venv not found. Run scripts\setup-api.ps1 first."
}

$env:PYTHONPATH = Join-Path $Root "apps\api"
Set-Location (Join-Path $Root "apps\api")
& $Python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
