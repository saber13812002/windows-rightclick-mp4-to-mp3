param([switch]$Force)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistDir = Join-Path $RepoRoot "dist"
$BuildDir = Join-Path $RepoRoot "build"
$SpecDir = Join-Path $RepoRoot "build"

function Write-Status {
    param([string]$Message)
    Write-Host ">>> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "OK $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "!! $Message" -ForegroundColor Yellow
}

function Find-Python {
    $candidates = @("python", "python3", "py")
    foreach ($cmd in $candidates) {
        $result = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($result) {
            return $result.Source
        }
    }
    return $null
}

$pythonExe = Find-Python
if (-not $pythonExe) {
    Write-Warning "Python not found. Please install Python 3 first."
    Write-Warning "Download from: https://www.python.org/downloads/"
    exit 1
}

Write-Status "Using Python: $pythonExe"

Write-Status "Checking PyInstaller..."
& $pythonExe -c "import PyInstaller" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Status "Installing PyInstaller via pip..."
    & $pythonExe -m pip install pyinstaller --quiet
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install PyInstaller."
    }
    Write-Success "PyInstaller installed."
} else {
    Write-Success "PyInstaller already installed."
}

$Scripts = @(
    @{Name="convert_mp4_to_mp3"; Source="convert-mp4-to-mp3/convert_mp4_to_mp3.py"}
    @{Name="convert_m4a_to_mp3"; Source="convert-m4a-to-mp3/convert_m4a_to_mp3.py"}
    @{Name="convert_to_ogg"; Source="convert-to-ogg/convert_to_ogg.py"}
    @{Name="batch_convert"; Source="batch-convert/batch_convert.py"}
    @{Name="split_middle_overlap"; Source="split-mp4-middle/split_middle_overlap.py"}
    @{Name="remove_silence"; Source="remove-silence-mp3/remove_silence.py"}
    @{Name="remove_long_silence"; Source="remove-long-silence-mp3/remove_long_silence.py"}
    @{Name="split_on_silence"; Source="split-on-silence-mp3/split_on_silence.py"}
    @{Name="setup"; Source="setup.py"}
)

Write-Status "Compiling scripts with PyInstaller (onefile mode)..."
if (Test-Path $BuildDir) {
    Remove-Item -Path $BuildDir -Recurse -Force
}
Get-ChildItem -Path $RepoRoot -Filter "*.spec" | Remove-Item -Force -ErrorAction SilentlyContinue

foreach ($s in $Scripts) {
    $name = $s.Name
    $source = Join-Path $RepoRoot $s.Source
    if (-not (Test-Path $source)) {
        Write-Warning "Source not found: $source -- skipping"
        continue
    }
    Write-Status "Compiling '$name'..."
    $pyArgs = @("--onefile", "--distpath", $DistDir, "--specpath", $SpecDir, "--workpath", $BuildDir, "--paths", $RepoRoot, "--name", $name, "--noconfirm", "--log-level", "WARN", $source)
    & $pythonExe -m PyInstaller @pyArgs
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed for $name"
    }
    Write-Success "Compiled: $name.exe"
}

$FfmpegDir = Join-Path $DistDir "ffmpeg"
$FfmpegExe = Join-Path $FfmpegDir "ffmpeg.exe"
$FfprobeExe = Join-Path $FfmpegDir "ffprobe.exe"

if ((Test-Path $FfmpegExe) -and (Test-Path $FfprobeExe) -and (-not $Force)) {
    Write-Success "FFmpeg already bundled in dist/ffmpeg/"
} else {
    Write-Status "Downloading FFmpeg (essentials portable build)..."
    $FfmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    $FfmpegZip = Join-Path $env:TEMP "ffmpeg-release-essentials.zip"
    Invoke-WebRequest -Uri $FfmpegUrl -OutFile $FfmpegZip -UseBasicParsing
    Write-Success "Downloaded FFmpeg zip"
    Write-Status "Extracting ffmpeg.exe + ffprobe.exe to dist/ffmpeg/ ..."
    $tempExtract = Join-Path $env:TEMP "ffmpeg_extract_temp"
    New-Item -ItemType Directory -Path $tempExtract -Force | Out-Null
    try {
        Expand-Archive -Path $FfmpegZip -DestinationPath $tempExtract -Force
        $binDirs = Get-ChildItem -Path $tempExtract -Recurse -Directory
        $binDir = $binDirs | Where-Object { $_.Name -eq "bin" } | Select-Object -First 1
        if (-not $binDir) {
            throw "Could not find bin/ inside FFmpeg archive."
        }
        New-Item -ItemType Directory -Path $FfmpegDir -Force | Out-Null
        Copy-Item (Join-Path $binDir.FullName "ffmpeg.exe") $FfmpegExe -Force
        Copy-Item (Join-Path $binDir.FullName "ffprobe.exe") $FfprobeExe -Force
        Write-Success "FFmpeg extracted to dist/ffmpeg/"
    } finally {
        Remove-Item -Path $tempExtract -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -Path $FfmpegZip -Force -ErrorAction SilentlyContinue
    }
}

Write-Status "Copying additional files to dist/..."
$AddMusicSource = Join-Path $RepoRoot "add-music-to-mp3"
$AddMusicDest = Join-Path $DistDir "add-music-to-mp3"
if (Test-Path $AddMusicSource) {
    New-Item -ItemType Directory -Path $AddMusicDest -Force | Out-Null
    Copy-Item (Join-Path $AddMusicSource "*") $AddMusicDest -Recurse -Force
    Write-Success "Copied add-music-to-mp3/"
}
Copy-Item (Join-Path $RepoRoot "install.bat") $DistDir -Force
Copy-Item (Join-Path $RepoRoot "uninstall.bat") $DistDir -Force
Write-Success "Copied install.bat + uninstall.bat"

Remove-Item -Path $BuildDir -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $RepoRoot -Filter "*.spec" | Remove-Item -Force -ErrorAction SilentlyContinue

$totalSize = Get-ChildItem -Path $DistDir -Recurse | Measure-Object -Property Length -Sum
$sizeMB = "{0:N1} MB" -f ($totalSize.Sum / 1MB)
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  Build complete!"
Write-Host "  Output folder: $DistDir"
Write-Host ""
Write-Host "  Total size: $sizeMB"
Write-Host ""
Write-Host "  To distribute:"
Write-Host "    1. Zip the entire dist/ folder"
Write-Host "    2. On target machine: unzip, right-click install.bat - Run as Administrator"
Write-Host ""
Write-Host "  End users do NOT need Python or FFmpeg installed."
Write-Host "================================================================" -ForegroundColor Green
