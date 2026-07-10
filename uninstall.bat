@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo    Windows Right-Click MP4/MP3 Tools - Uninstaller
echo ============================================================
echo.

REM ─── Check admin rights; elevate if needed ─────────────────────────────
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%~dpnx0' -ArgumentList '--elevated'"
    exit /b 0
)

echo [1/2] Removing registry entries...

REM ─── Registry keys to remove (must match setup.py entries) ─────────────
set "KEYS_TO_REMOVE="Convert to MP3" "Convert to OGG 48kHz" "Split midpoint (1s overlap)" "Add Custom Music" "Remove Silence (2s+)" "Remove Long Silence (5s+)" "Split on Silence (2s+)" "Convert all in folder to MP3" "Convert all in folder to OGG 48kHz" "Split midpoint for all in folder" "Remove silence for all in folder" "Remove long silence for all in folder" "Split on silence for all in folder""

REM ─── File type associations ─────────────────────────────────────────────
set "EXTENSIONS=.mp4 .m4a .mkv .avi .webm .mov .mp3"

for %%E in (%EXTENSIONS%) do (
    for %%K in (%KEYS_TO_REMOVE%) do (
        reg delete "HKEY_CLASSES_ROOT\SystemFileAssociations\%%E\shell\%%~K" /f >nul 2>&1
    )
)

REM ─── Directory right-click entries ─────────────────────────────────────
for %%K in (%KEYS_TO_REMOVE%) do (
    reg delete "HKEY_CLASSES_ROOT\Directory\shell\%%~K" /f >nul 2>&1
)

echo [2/2] Registry cleanup complete.
echo.
echo ============================================================
echo    ✓ All context menu entries have been removed!
echo ============================================================
echo.
echo   You can now delete this folder manually if desired.
echo.
pause
