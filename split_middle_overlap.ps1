#Requires -Version 5.0
param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Format-TimeSpan {
    param([double]$seconds)
    if ($seconds -lt 0) { $seconds = 0 }
    $ts = [TimeSpan]::FromSeconds($seconds)
    # ffmpeg accepts hh:mm:ss.mmm
    return '{0:00}:{1:00}:{2:00}.{3:000}' -f [int]$ts.TotalHours, $ts.Minutes, $ts.Seconds, $ts.Milliseconds
}

if (-not (Test-Path -LiteralPath $InputPath)) {
    Write-Error "File not found: $InputPath"
}

$fullPath = (Resolve-Path -LiteralPath $InputPath).Path
$dir = Split-Path -LiteralPath $fullPath -Parent
$base = [System.IO.Path]::GetFileNameWithoutExtension($fullPath)
$ext = [System.IO.Path]::GetExtension($fullPath)

# Ensure ffprobe/ffmpeg exist in PATH
foreach ($tool in @('ffprobe','ffmpeg')) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Error "$tool was not found in PATH. Please install FFmpeg and ensure it's accessible."
    }
}

# Get duration in seconds (floating)
$ffprobeArgs = @(
    '-v','error',
    '-show_entries','format=duration',
    '-of','default=noprint_wrappers=1:nokey=1',
    '--',
    $fullPath
)
$durationStr = & ffprobe @ffprobeArgs 2>$null
if (-not $durationStr) {
    Write-Error 'Could not read duration via ffprobe.'
}

[double]$duration = 0
if (-not [double]::TryParse($durationStr, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$duration)) {
    Write-Error "Invalid duration returned by ffprobe: $durationStr"
}

if ($duration -le 0) {
    Write-Error 'Media duration is zero or invalid.'
}

# Compute times
$midpoint = $duration / 2.0
$start2 = [Math]::Max($midpoint - 1.0, 0.0) # 1s overlap

$t1 = Format-TimeSpan -seconds $midpoint
$ss2 = Format-TimeSpan -seconds $start2

$out1 = Join-Path -Path $dir -ChildPath ("{0}_part1{1}" -f $base, $ext)
$out2 = Join-Path -Path $dir -ChildPath ("{0}_part2{1}" -f $base, $ext)

Write-Host "Input : $fullPath"
Write-Host ("Duration: {0:N3}s, Midpoint: {1:N3}s, Part2 starts at: {2:N3}s" -f $duration, $midpoint, $start2)
Write-Host "Output1: $out1"
Write-Host "Output2: $out2"

# Part 1: from 0 to midpoint
$ffmpegPart1 = @(
    '-y',
    '-hide_banner','-loglevel','error',
    '-i', $fullPath,
    '-t', $t1,
    '-c','copy',
    '--',
    $out1
)
& ffmpeg @ffmpegPart1

# Part 2: from (midpoint-1s) to end
$ffmpegPart2 = @(
    '-y',
    '-hide_banner','-loglevel','error',
    '-ss', $ss2,
    '-i', $fullPath,
    '-c','copy',
    '--',
    $out2
)
& ffmpeg @ffmpegPart2

Write-Host 'Done.' -ForegroundColor Green


