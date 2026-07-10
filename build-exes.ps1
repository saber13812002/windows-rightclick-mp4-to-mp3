<#
.SYNOPSIS
    Compile all Python scripts into standalone EXEs using PyInstaller,
    download portable FFmpeg, and prepare the dist/ folder for distribution.
    
    After running this, you can distribute the dist/ folder anywhere.
    End users just need to run: install.bat (as Administrator)
.NOTES
    Requires Python 3 and pip to be installed on the BUILD machine.
    The built EXEs do NOT require Python on the target machine.
#>

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistDir   = Join-Path $RepoRoot "dist"
$BuildDir  = Join-Path $RepoRoot "build"
$SpecDir   = Join-Path $RepoRoot "build"

# ─── helpers ────────────────────────────────────────────────────────────────
function Write-Status  { param([string]$Message) Write-Host ">>> $Message" -ForegroundColor Cyan }
function Write-Success { param([string]$Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }

# ─── 1. Ensure PyInstaller is installed ─────────────────────────────────────
Write-Status "Checking PyInstaller..."
$pyInstalled = & python -c "import PyInstaller; print('ok')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Status "Installing PyInstaller via pip..."
    python -m pip install pyinstaller --quiet
    if ($LASTEXITCODE -ne 0) { throw "Failed to install PyInstaller." }
    Write-Success "PyInstaller installed."
} else {
    Write-Success "PyInstaller already installed."
}

# ─── 2. Define scripts to compile ──────────────────────────────────────────
$Scripts = @(
    @{ Name = "convert_mp4_to_mp3";       Source = "convert-mp4-to-mp3\convert_mp4_to_mp3.py" }
    @{ Name = "convert_m4a_to_mp3";       Source = "convert-m4a-to-mp3\convert_m4a_to_mp3.py" }
    @{ Name = "convert_to_ogg";           Source = "convert-to-ogg\convert_to_ogg.py" }
    @{ Name = "batch_convert";            Source = "batch-convert\batch_convert.py" }
    @{ Name = "split_middle_overlap";     Source = "split-mp4-middle\split_middle_overlap.py" }
    @{ Name = "remove_silence";           Source = "remove-silence-mp3\remove_silence.py" }
    @{ Name = "remove_long_silence";      Source = "remove-long-silence-mp3\remove_long_silence.py" }
    @{ Name = "split_on_silence";         Source = "split-on-silence-mp3\split_on_silence.py" }
    @{ Name = "setup";                    Source = "setup.py" }
)

# ─── 3. Compile each script with PyInstaller ───────────────────────────────
Write-Status "Compiling scripts with PyInstaller (onefile mode)..."

# Clean previous builds
if (Test-Path $BuildDir) { Remove-Item -Path $BuildDir -Recurse -Force }
Remove-Item -Path "$RepoRoot\*.spec" -Force -ErrorAction SilentlyContinue

foreach ($s in $Scripts) {
    $name   = $s.Name
    $source = Join-Path $RepoRoot $s.Source

    if (-not (Test-Path $source)) {
        Write-Warning "Source not found: $source — skipping"
        continue
    }

    Write-Status "Compiling '$name'..."
    $outDir = Join-Path $DistDir $name
    pyinstaller --onefile `
        --distpath $DistDir `
        --specpath $SpecDir `
        --workpath $BuildDir `
        --paths $RepoRoot `
        --name $name `
        --noconfirm `
        --log-level WARN `
        $source

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed for $name"
    }
    Write-Success "Compiled: $name.exe"
}

# ─── 4. Download / bundle FFmpeg ──────────────────────────────────────────
$FfmpegDir = Join-Path $DistDir "ffmpeg"
$FfmpegExe  = Join-Path $FfmpegDir "ffmpeg.exe"
$FfprobeExe = Join-Path $FfmpegDir "ffprobe.exe"

if ((Test-Path $FfmpegExe) -and (Test-Path $FfprobeExe) -and (-not $Force)) {
    Write-Success "FFmpeg already bundled in dist/ffmpeg/"
} else {
    Write-Status "Downloading FFmpeg (essentials portable build)..."
    $FfmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    $FfmpegZip = Join-Path $env:TEMP "ffmpeg-release-essentials.zip"

    Invoke-WebRequest -Uri $FfmpegUrl -OutFile $FfmpegZip -UseBasicParsing
    Write-Success "Downloaded FFmpeg zip"

    Write-Status "Extracting ffmpeg.exe + ffprobe.exe → dist/ffmpeg/ ..."
    $tempExtract = Join-Path $env:TEMP "ffmpeg_extract_$([System.Guid]::NewGuid().ToString('N'))"
    New-Item -ItemType Directory -Path $tempExtract -Force | Out-Null
    try {
        Expand-Archive -Path $FfmpegZip -DestinationPath $tempExtract -Force
        $binDir = Get-ChildItem -Path $tempExtract -Recurse -Directory `
            | Where-Object { $_.Name -eq "bin" } `
            | Select-Object -First 1
        if (-not $binDir) { throw "Could not find bin/ inside FFmpeg archive." }

        New-Item -ItemType Directory -Path $FfmpegDir -Force | Out-Null
        Copy-Item (Join-Path $binDir.FullName "ffmpeg.exe")  $FfmpegExe  -Force
        Copy-Item (Join-Path $binDir.FullName "ffprobe.exe") $FfprobeExe -Force
        Write-Success "FFmpeg extracted to dist/ffmpeg/"
    }
    finally {
        Remove-Item -Path $tempExtract -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -Path $FfmpegZip -Force -ErrorAction SilentlyContinue
    }
}

# ─── 5. Copy additional files into dist/ ───────────────────────────────────
Write-Status "Copying additional files to dist/..."

# add-music-to-mp3 folder (batch + audio files)
$AddMusicDest = Join-Path $DistDir "add-music-to-mp3"
if (Test-Path (Join-Path $RepoRoot "add-music-to-mp3")) {
    New-Item -ItemType Directory -Path $AddMusicDest -Force | Out-Null
    Copy-Item (Join-Path $RepoRoot "add-music-to-mp3\*") $AddMusicDest -Recurse -Force
    Write-Success "Copied add-music-to-mp3/"
}

# install.bat and uninstall.bat
Copy-Item (Join-Path $RepoRoot "install.bat")   $DistDir -Force
Copy-Item (Join-Path $RepoRoot "uninstall.bat") $DistDir -Force
Write-Success "Copied install.bat + uninstall.bat"

# ─── 6. Clean up build artifacts ──────────────────────────────────────────
Remove-Item -Path $BuildDir -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $RepoRoot -Filter "*.spec" | Remove-Item -Force -ErrorAction SilentlyContinue

# ─── 7. Summary ───────────────────────────────────────────────────────────
Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Build complete!" -ForegroundColor Green
Write-Host "  Output folder: $DistDir" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "  Total size: $(Get-ChildItem -Path $DistDir -Recurse | Measure-Object -Property Length -Sum | ForEach-Object { '{0:N1} MB' -f ($_.Sum / 1MB) })" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "  To distribute:" -ForegroundColor Yellow
Write-Host "    1. Zip the entire dist/ folder" -ForegroundColor White
Write-Host "    2. On target machine: unzip, right-click install.bat → Run as Administrator" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "  End users do NOT need Python or FFmpeg installed." -ForegroundColor Green
Write-Host "══════════════════════════════════════════════════════════════" -ForegroundColor Green
