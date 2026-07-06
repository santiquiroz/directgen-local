$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$ApiScript = Join-Path $Root "scripts\start-api.ps1"
$WebScript = Join-Path $Root "scripts\start-web.ps1"

Start-Process powershell -WorkingDirectory $Root -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $ApiScript
)

Start-Sleep -Seconds 4

Start-Process powershell -WorkingDirectory (Join-Path $Root "apps\web") -ArgumentList @(
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $WebScript
)

Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:5173"
