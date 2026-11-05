@echo off
cd /d "%~dp0"
set "PYTHONPATH=%~dp0..\..\work\python_packages"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m streamlit run app.py --global.developmentMode false --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
) else (
  python -m streamlit run app.py --global.developmentMode false --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
)
pause
