@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ─── config ───────────────────────────────────────────────────────────────
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

REM ─── 2. Check dependencies ─────────────────────────────────────────────
echo [1/4] Checking dependencies...

if exist "%SCRIPT_DIR%python\python.exe" (
    echo   ✓ Bundled Python found
    set "PY=%SCRIPT_DIR%python\python.exe"
) else (
    set "PY="
    for /f "delims=" %%i in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%i"
    if defined PY (
        echo   ✓ Python found via py launcher
    ) else (
        for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PY=%%i"
        if defined PY (
            echo   ✓ Python found in PATH
        )
    )
)

if not defined PY (
    echo   ✗ Python not found!
    echo.
    echo   Please install Python 3 or run download-deps.ps1 first.
    echo   Right-click download-deps.ps1 ^> "Run with PowerShell"
    echo.
    pause
    exit /b 1
)

if exist "%SCRIPT_DIR%ffmpeg\ffmpeg.exe" (
    echo   ✓ Bundled FFmpeg found
) else (
    echo   ⚠ Bundled FFmpeg not found (will try PATH)
)

echo.

REM ─── 3. Run setup ──────────────────────────────────────────────────────
echo [2/4] Running setup to generate registry file...
if exist "%SCRIPT_DIR%ffmpeg\ffmpeg.exe" (
    "%PY%" "%SCRIPT_DIR%setup.py" --python "%PY%" --ffmpeg "%SCRIPT_DIR%ffmpeg\ffmpeg.exe"
) else (
    "%PY%" "%SCRIPT_DIR%setup.py" --python "%PY%"
)

if %errorlevel% neq 0 (
    echo   ✗ Setup failed!
    pause
    exit /b 1
)
echo   ✓ Setup complete
echo.

REM ─── 4. Import registry ────────────────────────────────────────────────
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

REM ─── 5. Done ───────────────────────────────────────────────────────────
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
