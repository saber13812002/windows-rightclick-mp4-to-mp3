<#
.SYNOPSIS
    Download and extract portable FFmpeg + Embedded Python for this project.
    Run this once before install.bat on a fresh Windows system.
.DESCRIPTION
    Downloads FFmpeg (essentials portable build) and Embedded Python,
    extracts them into ffmpeg/ and python/ folders under the project root.
.NOTES
    Requires internet connection. Run with PowerShell.
    Usage: .\download-deps.ps1
#>

param(
    [string]$PythonVersion = "3.11.9",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"  # faster downloads

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# ─── helpers ────────────────────────────────────────────────────────────────
function Write-Status {
    param([string]$Message)
    Write-Host ">>> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Test-ToolExists {
    param([string]$Path)
    return (Test-Path -LiteralPath $Path -PathType Leaf)
}

# ─── 1. Download / extract FFmpeg ──────────────────────────────────────────
$FfmpegDir = Join-Path $RepoRoot "ffmpeg"
$FfmpegExe  = Join-Path $FfmpegDir "ffmpeg.exe"
$FfprobeExe = Join-Path $FfmpegDir "ffprobe.exe"

if ((Test-ToolExists $FfmpegExe) -and (Test-ToolExists $FfprobeExe)) -and (-not $Force) {
    Write-Success "FFmpeg already present at '$FfmpegDir' (use -Force to re-download)"
} else {
    Write-Status "Downloading FFmpeg (essentials portable build)..."
    $FfmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    $FfmpegZip = Join-Path $env:TEMP "ffmpeg-release-essentials.zip"

    try {
        Invoke-WebRequest -Uri $FfmpegUrl -OutFile $FfmpegZip -UseBasicParsing
        Write-Success "Downloaded FFmpeg zip ($([math]::Round((Get-Item $FfmpegZip).Length / 1MB, 1)) MB)"

        Write-Status "Extracting FFmpeg (ffmpeg.exe + ffprobe.exe) → 'ffmpeg/' ..."
        # The zip contains a subfolder like ffmpeg-*-essentials_build/bin/
        $tempExtract = Join-Path $env:TEMP "ffmpeg_extract_$([System.Guid]::NewGuid().ToString('N'))"
        New-Item -ItemType Directory -Path $tempExtract -Force | Out-Null
        try {
            Expand-Archive -Path $FfmpegZip -DestinationPath $tempExtract -Force

            # Find the bin/ folder inside the extracted archive
            $binDir = Get-ChildItem -Path $tempExtract -Recurse -Directory `
                | Where-Object { $_.Name -eq "bin" } `
                | Select-Object -First 1

            if (-not $binDir) {
                throw "Could not find bin/ directory inside FFmpeg archive."
            }

            # Ensure target directory exists
            New-Item -ItemType Directory -Path $FfmpegDir -Force | Out-Null

            # Copy the two executables
            Copy-Item (Join-Path $binDir.FullName "ffmpeg.exe") $FfmpegExe -Force
            Copy-Item (Join-Path $binDir.FullName "ffprobe.exe") $FfprobeExe -Force

            Write-Success "FFmpeg extracted to '$FfmpegDir'"
        }
        finally {
            Remove-Item -Path $tempExtract -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    catch {
        Write-Warning "FFmpeg download/extract failed: $_"
        Write-Warning "You can manually download from: $FfmpegUrl"
        Write-Warning "Extract ffmpeg.exe + ffprobe.exe into the 'ffmpeg/' folder."
    }
    finally {
        Remove-Item -Path $FfmpegZip -Force -ErrorAction SilentlyContinue
    }
}

# ─── 2. Download / extract Embedded Python ─────────────────────────────────
$PythonDir = Join-Path $RepoRoot "python"
$PythonExe = Join-Path $PythonDir "python.exe"

if ((Test-ToolExists $PythonExe)) -and (-not $Force) {
    Write-Success "Embedded Python already present at '$PythonDir' (use -Force to re-download)"
} else {
    Write-Status "Downloading Embedded Python $PythonVersion ..."
    $PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
    $PythonZip = Join-Path $env:TEMP "python-$PythonVersion-embed-amd64.zip"

    try {
        Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonZip -UseBasicParsing
        Write-Success "Downloaded Python zip ($([math]::Round((Get-Item $PythonZip).Length / 1MB, 1)) MB)"

        Write-Status "Extracting Embedded Python → 'python/' ..."
        New-Item -ItemType Directory -Path $PythonDir -Force | Out-Null
        Expand-Archive -Path $PythonZip -DestinationPath $PythonDir -Force

        # Enable site-packages by editing python._pth
        $PthFile = Get-ChildItem -Path $PythonDir -Filter "python*._pth" | Select-Object -First 1
        if ($PthFile) {
            $pthContent = Get-Content -Path $PthFile.FullName -Raw
            if ($pthContent -match "^#import site") {
                $pthContent = $pthContent -replace "^#import site", "import site"
                Set-Content -Path $PthFile.FullName -Value $pthContent
                Write-Success "Enabled 'import site' in $($PthFile.Name)"
            } elseif ($pthContent -notmatch "^import site") {
                # Add import site line
                $pthContent = $pthContent.TrimEnd() + "`r`nimport site`r`n"
                Set-Content -Path $PthFile.FullName -Value $pthContent
                Write-Success "Added 'import site' to $($PthFile.Name)"
            } else {
                Write-Success "'import site' already enabled in $($PthFile.Name)"
            }
        }

        Write-Success "Embedded Python extracted to '$PythonDir'"
    }
    catch {
        Write-Warning "Python download/extract failed: $_"
        Write-Warning "You can manually download from: $PythonUrl"
        Write-Warning "Extract all files into the 'python/' folder."
        Write-Warning "Then edit python\python._pth: uncomment '#import site' (remove the #)."
    }
    finally {
        Remove-Item -Path $PythonZip -Force -ErrorAction SilentlyContinue
    }
}

# ─── 3. Verify ─────────────────────────────────────────────────────────────
Write-Status "Verifying downloaded components..."
$allOk = $true

if (Test-ToolExists $FfmpegExe) {
    try {
        $ver = & $FfmpegExe -version 2>&1 | Select-Object -First 1
        Write-Success "FFmpeg: $ver"
    } catch {
        Write-Warning "FFmpeg binary found but couldn't run it."
    }
} else {
    Write-Warning "ffmpeg.exe missing in '$FfmpegDir'"
    $allOk = $false
}

if (Test-ToolExists $FfprobeExe) {
    Write-Success "ffprobe.exe present"
} else {
    Write-Warning "ffprobe.exe missing in '$FfmpegDir'"
    $allOk = $false
}

if (Test-ToolExists $PythonExe) {
    try {
        $ver = & $PythonExe --version 2>&1
        Write-Success "Python: $ver"
    } catch {
        Write-Warning "Python binary found but couldn't run it."
    }
} else {
    Write-Warning "python.exe missing in '$PythonDir'"
    $allOk = $false
}

Write-Host ""
if ($allOk) {
    Write-Host "══════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  All dependencies ready!" -ForegroundColor Green
    Write-Host "  Next step: right-click and run as Administrator:" -ForegroundColor White
    Write-Host "    install.bat" -ForegroundColor Yellow
    Write-Host "══════════════════════════════════════════════" -ForegroundColor Green
} else {
    Write-Host "══════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "  Some components are missing." -ForegroundColor Yellow
    Write-Host "  Check warnings above and re-run or download manually." -ForegroundColor White
    Write-Host "══════════════════════════════════════════════" -ForegroundColor Yellow
}

if (-not $allOk) { exit 1 }
