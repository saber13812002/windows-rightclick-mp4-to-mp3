@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
set "PY="
for /f "delims=" %%i in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%i"
if not defined PY for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%i"
if not defined PY (
    echo Python not found. Run from folder that has Python, or: python setup.py --check
    pause
    exit /b 1
)
"%PY%" "%SCRIPT_DIR%setup.py" --check
echo.
pause
