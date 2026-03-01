@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "PY="
for /f "delims=" %%i in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%i"
if not defined PY for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%i"
if not defined PY (
    echo Python not found in PATH.
    set /p "PY=Enter full path to python.exe: "
    set "PY=!PY:"=!"
)
if not defined PY (
    echo Aborted.
    pause
    exit /b 1
)

echo Using Python: %PY%
"%PY%" "%SCRIPT_DIR%setup.py" --python "%PY%"
echo.
pause
