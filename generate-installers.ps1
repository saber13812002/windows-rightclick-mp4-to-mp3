Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-PythonExecutable {
    $pyCandidate = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCandidate) {
        try {
            $detected = & $pyCandidate.Source -3 -c "import sys; print(sys.executable)" 2>$null
            if ($LASTEXITCODE -eq 0 -and $detected) {
                return $detected.Trim()
            }
        } catch {
            Write-Verbose ("Failed to query python via 'py -3': {0}" -f $_)
        }
    }

    foreach ($name in @('python', 'python3')) {
        $candidate = Get-Command $name -ErrorAction SilentlyContinue
        if ($candidate) {
            try {
                & $candidate.Source --version *> $null
                if ($LASTEXITCODE -eq 0) {
                    return $candidate.Source
                }
            } catch {
                Write-Verbose ("Failed to validate {0}: {1}" -f $name, $_)
            }
        }
    }

    Write-Host "Python executable could not be auto-detected."
    $manual = Read-Host "Enter full path to python.exe (leave empty to abort)"
    if ([string]::IsNullOrWhiteSpace($manual)) {
        throw "Python executable path not provided."
    }
    if (!(Test-Path -Path $manual -PathType Leaf)) {
        throw "Provided python path '$manual' was not found."
    }
    return (Resolve-Path $manual).ProviderPath
}

function ConvertTo-RegValue([string]$value) {
    return $value.Replace('\', '\\').Replace('"', '\"')
}

function New-RegBlock {
    param(
        [string]$Extension,
        [string]$MenuText,
        [string]$Command,
        [string]$Comment,
        [switch]$IncludeHeader
    )

    $lines = New-Object System.Collections.Generic.List[string]
    if ($IncludeHeader) {
        $lines.Add('Windows Registry Editor Version 5.00')
        $lines.Add('')
    }
    if ($Comment) {
        $lines.Add("; $Comment")
        $lines.Add('')
    }

    $key = "[HKEY_CLASSES_ROOT\SystemFileAssociations\$Extension\shell\$MenuText]"
    $lines.Add($key)
    $lines.Add("@=""{0}""" -f $MenuText)
    $lines.Add('')
    $lines.Add("[$key\command]")
    $escapedCommand = ConvertTo-RegValue $Command
    $lines.Add("@=""{0}""" -f $escapedCommand)
    $lines.Add('')
    return $lines -join "`r`n"
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$tools = @(
    @{
        Name = 'convert-mp4-to-mp3'
        Extension = '.mp4'
        MenuText = 'Convert to MP3'
        Comment = 'Adds a context menu entry to convert MP4 to MP3.'
        Script = 'convert-mp4-to-mp3\convert_mp4_to_mp3.py'
        OutputReg = 'convert-mp4-to-mp3\convert to mp3.reg'
        RequiresPython = $true
    },
    @{
        Name = 'convert-m4a-to-mp3'
        Extension = '.m4a'
        MenuText = 'Convert to MP3'
        Comment = 'Adds a context menu entry to convert M4A to MP3.'
        Script = 'convert-m4a-to-mp3\convert_m4a_to_mp3.py'
        OutputReg = 'convert-m4a-to-mp3\add_right_click_m4a.reg'
        RequiresPython = $true
    },
    @{
        Name = 'split-mp4-middle'
        Extension = '.mp4'
        MenuText = 'Split midpoint (1s overlap)'
        Comment = 'Splits MP4 files at the midpoint with a 1 second overlap.'
        Script = 'split-mp4-middle\split_middle_overlap.py'
        OutputReg = 'split-mp4-middle\add_right_click_split_middle_python.reg'
        RequiresPython = $true
    },
    @{
        Name = 'split-mp3-middle'
        Extension = '.mp3'
        MenuText = 'Split midpoint (1s overlap)'
        Comment = 'Splits MP3 files at the midpoint with a 1 second overlap.'
        Script = 'split-mp4-middle\split_middle_overlap.py'
        OutputReg = 'split-mp3-middle\add_right_click_split_middle_python_mp3.reg'
        RequiresPython = $true
    },
    @{
        Name = 'add-music-to-mp3'
        Extension = '.mp3'
        MenuText = 'Add Custom Music'
        Comment = 'Runs add_music.bat to attach intro/middle/outro tracks.'
        Script = 'add-music-to-mp3\add_music.bat'
        OutputReg = 'add-music-to-mp3\add music.reg'
        RequiresPython = $false
    },
    @{
        Name = 'remove-silence-mp3'
        Extension = '.mp3'
        MenuText = 'Remove Silence (2s+)'
        Comment = 'Removes 2+ second silence segments from MP3 files.'
        Script = 'remove-silence-mp3\remove_silence.py'
        OutputReg = 'remove-silence-mp3\remove_silence.reg'
        RequiresPython = $true
    },
    @{
        Name = 'remove-long-silence-mp3'
        Extension = '.mp3'
        MenuText = 'Remove Long Silence (5s+)'
        Comment = 'Removes 5+ second silence segments from MP3 files.'
        Script = 'remove-long-silence-mp3\remove_long_silence.py'
        OutputReg = 'remove-long-silence-mp3\remove_long_silence.reg'
        RequiresPython = $true
    },
    @{
        Name = 'split-on-silence-mp3'
        Extension = '.mp3'
        MenuText = 'Split on Silence (2s+)'
        Comment = 'Splits MP3 files into parts whenever a 2+ second silence occurs.'
        Script = 'split-on-silence-mp3\split_on_silence.py'
        OutputReg = 'split-on-silence-mp3\split_on_silence.reg'
        RequiresPython = $true
    }
)

$pythonPath = $null
if ($tools.Where({ $_.RequiresPython }).Count -gt 0) {
    $pythonPath = Get-PythonExecutable
    $pythonPath = (Resolve-Path $pythonPath).ProviderPath
}

$aggregateBlocks = New-Object System.Collections.Generic.List[string]

foreach ($tool in $tools) {
    $scriptPath = Join-Path $repoRoot $tool.Script
    if (!(Test-Path -LiteralPath $scriptPath)) {
        throw "Script '$($tool.Script)' was not found."
    }
    $scriptPath = (Resolve-Path $scriptPath).ProviderPath
    $command = if ($tool.RequiresPython) {
        "`"$pythonPath`" `"$scriptPath`" `"%1`""
    } else {
        "`"$scriptPath`" `"%1`""
    }

    $regContent = New-RegBlock -Extension $tool.Extension `
        -MenuText $tool.MenuText `
        -Command $command `
        -Comment $tool.Comment `
        -IncludeHeader

    $outputFile = Join-Path $repoRoot $tool.OutputReg
    $outputDir = Split-Path $outputFile -Parent
    if (!(Test-Path -LiteralPath $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir | Out-Null
    }
    Set-Content -LiteralPath $outputFile -Value $regContent -Encoding Unicode

    $block = New-RegBlock -Extension $tool.Extension `
        -MenuText $tool.MenuText `
        -Command $command `
        -Comment $tool.Comment
    $aggregateBlocks.Add($block)
}

$masterRegPath = Join-Path $repoRoot 'install-all-tools.reg'
$masterContent = "Windows Registry Editor Version 5.00`r`n`r`n" + ($aggregateBlocks -join "`r`n")
Set-Content -LiteralPath $masterRegPath -Value $masterContent -Encoding Unicode

Write-Host "Updated $($tools.Count) registry scripts plus master install-all-tools.reg"

