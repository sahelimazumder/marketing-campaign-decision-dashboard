$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$workspacePackages = Join-Path $PSScriptRoot '..\..\work\python_packages'
if (Test-Path -LiteralPath $workspacePackages) {
    $env:PYTHONPATH = (Resolve-Path -LiteralPath $workspacePackages).Path
    python -m streamlit run app.py --global.developmentMode false --browser.gatherUsageStats false
} elseif (Test-Path -LiteralPath '.venv\Scripts\python.exe') {
    & '.\.venv\Scripts\python.exe' -m streamlit run app.py --global.developmentMode false --browser.gatherUsageStats false
} else {
    Write-Host 'Follow README.md to install dependencies, then run this script again.'
}
