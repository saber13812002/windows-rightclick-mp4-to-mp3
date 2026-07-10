@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo ============================================================
echo    Windows Right-Click MP4/MP3 Tools - Installer
echo ============================================================
echo.

REM ─── 1. Check admin rights; elevate if needed ──────────────────────────
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%~dpnx0' -ArgumentList '--elevated'"
    exit /b 0
)

REM ─── 2. Detect setup method ────────────────────────────────────────────
echo [1/4] Detecting components...

if exist "%SCRIPT_DIR%setup.exe" (
    echo   ✓ Found compiled setup.exe
    set "SETUP_CMD=%SCRIPT_DIR%setup.exe"
    goto :run_setup
)

if exist "%SCRIPT_DIR%python\python.exe" (
    echo   ✓ Found bundled Python
    set "SETUP_CMD=%SCRIPT_DIR%python\python.exe "%SCRIPT_DIR%setup.py""
    goto :run_setup
)

set "PY="
for /f "delims=" %%i in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%i"
if defined PY (
    echo   ✓ Found Python via py launcher
    set "SETUP_CMD=""!PY!" "%SCRIPT_DIR%setup.py""
    goto :run_setup
)

for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%i"
if defined PY (
    echo   ✓ Found Python in PATH
    set "SETUP_CMD=""!PY!" "%SCRIPT_DIR%setup.py""
    goto :run_setup
)

echo   ✗ No Python, setup.exe, or bundled Python found!
echo.
echo   Please run build-exes.ps1 first to compile the EXEs,
echo   or install Python 3 and re-run this installer.
echo.
pause
exit /b 1

:run_setup

REM ─── 3. Detect bundled FFmpeg ──────────────────────────────────────────
set "FFMPEG_ARG="
if exist "%SCRIPT_DIR%ffmpeg\ffmpeg.exe" (
    echo   ✓ Bundled FFmpeg found
    set "FFMPEG_ARG=--ffmpeg "%SCRIPT_DIR%ffmpeg\ffmpeg.exe""
) else (
    echo   ⚠ Bundled FFmpeg not found (will try PATH)
)
echo.

REM ─── 4. Run setup ──────────────────────────────────────────────────────
echo [2/4] Generating registry file...
%SETUP_CMD% %FFMPEG_ARG%
if %errorlevel% neq 0 (
    echo   ✗ Setup failed!
    pause
    exit /b 1
)
echo   ✓ Registry file generated
echo.

REM ─── 5. Import registry ────────────────────────────────────────────────
echo [3/4] Importing registry entries...
if exist "%SCRIPT_DIR%register_all.reg" (
    reg import "%SCRIPT_DIR%register_all.reg"
    if !errorlevel! equ 0 (
        echo   ✓ Registry imported successfully
    ) else (
        echo   ✗ Registry import failed. Try manually:
        echo     Right-click register_all.reg ^> Merge
        pause
        exit /b 1
    )
) else (
    echo   ✗ register_all.reg not found!
    pause
    exit /b 1
)
echo.

REM ─── 6. Done ───────────────────────────────────────────────────────────
echo [4/4] Installation complete!
echo.
echo ============================================================
echo    ✓ All context menu entries have been added!
echo ============================================================
echo.
echo   Right-click on any:
echo     .mp4 file  - Convert to MP3 / OGG / Split
echo     .m4a file  - Convert to MP3 / OGG
echo     .mp3 file  - Split / Add Music / Remove Silence / Split on Silence
echo     Folder     - Batch convert all files
echo.
echo   To uninstall later, run: uninstall.bat (as Administrator)
echo.
pause
