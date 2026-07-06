$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Web = Join-Path $Root "apps\web"

if (!(Test-Path (Join-Path $Web "node_modules"))) {
    Set-Location $Web
    npm install
}

Set-Location $Web
npm run dev
