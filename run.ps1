# run.ps1 - helper to create virtualenv and run Streamlit app
param(
    [switch]$recreate,
    [int]$port = 8501
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $projectRoot

$venvPath = Join-Path $projectRoot ".venv"

if ($recreate -or -not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath..."
    python -m venv .venv
    Write-Host "Activating virtual environment and installing dependencies..."
    & "$venvPath\Scripts\Activate.ps1"
    pip install --upgrade pip
    pip install -r requirements-lock.txt
    pip install streamlit sqlalchemy
} else {
    Write-Host "Using existing virtual environment at $venvPath"
    & "$venvPath\Scripts\Activate.ps1"
}

Write-Host "Starting Streamlit app on http://127.0.0.1:$port"
streamlit run streamlit_app.py --server.port=$port --server.address=127.0.0.1
