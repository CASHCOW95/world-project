$ErrorActionPreference = "Stop"

$Root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$Frontend = Join-Path $Root "03_월드개발페이지\frontend"
$Backend = Join-Path $Root "03_월드개발페이지\backend"
$PythonEngine = Join-Path $Backend "core\styler_pro_engine"

Write-Host "== Python dependencies =="
python -m pip install -r (Join-Path $Root "requirements.txt")

Write-Host "== Python syntax =="
python -m compileall -q $PythonEngine

Write-Host "== Static JavaScript syntax =="
node --check (Join-Path $Frontend "js\main.js")
node --check (Join-Path $Frontend "build.js")
node --check (Join-Path $Backend "server.js")

Write-Host "== React/Vite production build =="
Push-Location $Frontend
try {
  npm run build
}
finally {
  Pop-Location
}

Write-Host "Validation complete."
