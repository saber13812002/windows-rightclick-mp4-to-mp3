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

set "FFMPEG_ARG="
"%PY%" -c "import shutil; exit(0 if shutil.which('ffmpeg') else 1)" 2>nul
if errorlevel 1 (
    echo ffmpeg not in PATH.
    set /p "FFMPEG=Enter path to ffmpeg.exe or its folder (e.g. paste from Explorer bar): "
    set "FFMPEG=!FFMPEG:"=!"
    if defined FFMPEG set "FFMPEG_ARG=--ffmpeg "!FFMPEG!""
)

"%PY%" "%SCRIPT_DIR%setup.py" --python "%PY%" %FFMPEG_ARG%
echo.
pause
