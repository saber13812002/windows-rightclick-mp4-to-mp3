@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM ─── اولویت ۱: پایتون باندل شده ───────────────────────────────────────────
if exist "%SCRIPT_DIR%python\python.exe" (
    set "PY=%SCRIPT_DIR%python\python.exe"
    echo Using bundled python: !PY!
    goto :run_setup
)

REM ─── اولویت ۲: py launcher ────────────────────────────────────────────────
set "PY="
for /f "delims=" %%i in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%i"
if defined PY goto :run_setup

REM ─── اولویت ۳: python from PATH ───────────────────────────────────────────
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%i"
if defined PY goto :run_setup

REM ─── اولویت ۴: از کاربر بپرس ─────────────────────────────────────────────
echo Python not found in PATH or bundled.
set /p "PY=Enter full path to python.exe: "
set "PY=!PY:"=!"
if not defined PY (
    echo Aborted.
    pause
    exit /b 1
)

:run_setup
echo Using Python: %PY%

REM ─── تشخیص ffmpeg باندل شده ──────────────────────────────────────────────
set "FFMPEG_ARG="
if exist "%SCRIPT_DIR%ffmpeg\ffmpeg.exe" (
    echo Using bundled ffmpeg.
    set "FFMPEG_ARG=--ffmpeg "%SCRIPT_DIR%ffmpeg\ffmpeg.exe""
    goto :exec_setup
)

REM ─── اگر ffmpeg در PATH نیست، از کاربر بپرس ──────────────────────────────
"%PY%" -c "import shutil; exit(0 if shutil.which('ffmpeg') else 1)" 2>nul
if errorlevel 1 (
    echo ffmpeg not in PATH or bundled.
    set /p "FFMPEG=Enter path to ffmpeg.exe or its folder (e.g. paste from Explorer bar): "
    set "FFMPEG=!FFMPEG:"=!"
    if defined FFMPEG set "FFMPEG_ARG=--ffmpeg "!FFMPEG!""
)

:exec_setup
"%PY%" "%SCRIPT_DIR%setup.py" --python "%PY%" %FFMPEG_ARG%
echo.
pause
