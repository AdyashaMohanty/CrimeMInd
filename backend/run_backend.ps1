$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
& "$PSScriptRoot\..\.venv311\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
