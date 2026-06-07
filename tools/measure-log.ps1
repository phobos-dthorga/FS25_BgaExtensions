param(
    [string]$LogPath,
    [string]$GameUserDir,
    [string]$SummaryJson = "dist\current-log-summary.json",
    [switch]$FailOnPhobosWarning
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$measureScript = Join-Path $PSScriptRoot "measure_log.py"

function Get-UniquePaths {
    param([string[]]$Paths)

    $seen = @{}
    $result = @()
    foreach ($path in $Paths) {
        if ([string]::IsNullOrWhiteSpace($path)) {
            continue
        }

        $key = $path.ToLowerInvariant()
        if ($seen.ContainsKey($key)) {
            continue
        }

        $seen[$key] = $true
        $result += $path
    }

    return $result
}

function Get-CandidateLogPaths {
    param([string]$ExplicitGameUserDir)

    $paths = @()

    if (-not [string]::IsNullOrWhiteSpace($ExplicitGameUserDir)) {
        $paths += Join-Path $ExplicitGameUserDir "log.txt"
    }

    if (-not [string]::IsNullOrWhiteSpace($env:FS25_LOG_PATH)) {
        $paths += $env:FS25_LOG_PATH
    }

    if (-not [string]::IsNullOrWhiteSpace($env:FS25_USER_DIR)) {
        $paths += Join-Path $env:FS25_USER_DIR "log.txt"
    }

    $documents = [Environment]::GetFolderPath("MyDocuments")
    if (-not [string]::IsNullOrWhiteSpace($documents)) {
        $paths += Join-Path $documents "My Games\FarmingSimulator2025\log.txt"
    }

    if (-not [string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
        $paths += Join-Path $env:USERPROFILE "Documents\My Games\FarmingSimulator2025\log.txt"
    }

    foreach ($envName in @("OneDrive", "OneDriveConsumer", "OneDriveCommercial")) {
        $oneDrive = [Environment]::GetEnvironmentVariable($envName)
        if (-not [string]::IsNullOrWhiteSpace($oneDrive)) {
            $paths += Join-Path $oneDrive "Documents\My Games\FarmingSimulator2025\log.txt"
        }
    }

    foreach ($startPath in @($repoRoot.Path, (Get-Location).Path)) {
        $current = Get-Item -LiteralPath $startPath
        while ($null -ne $current) {
            $paths += Join-Path $current.FullName "My Games\FarmingSimulator2025\log.txt"
            $current = $current.Parent
        }
    }

    return Get-UniquePaths -Paths $paths
}

function Resolve-FS25LogPath {
    param(
        [string]$ExplicitLogPath,
        [string]$ExplicitGameUserDir
    )

    if (-not [string]::IsNullOrWhiteSpace($ExplicitLogPath)) {
        return (Resolve-Path -LiteralPath $ExplicitLogPath).Path
    }

    $candidates = Get-CandidateLogPaths -ExplicitGameUserDir $ExplicitGameUserDir
    $existing = @($candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf })
    if ($existing.Count -eq 0) {
        Write-Error "FS25 log.txt was not found. Pass -LogPath or set FS25_LOG_PATH. Checked:`n$($candidates -join "`n")"
    }

    return @($existing | Sort-Object { (Get-Item -LiteralPath $_).LastWriteTimeUtc } -Descending)[0]
}

function Test-PhobosLine {
    param(
        [string]$Line,
        [string]$ModName = "FS25_BgaExtensions"
    )

    $lowered = $Line.ToLowerInvariant().Replace("\", "/")
    return (
        $lowered.Contains($ModName.ToLowerInvariant()) -or
        $lowered.Contains("/placeables/phobos/") -or
        $lowered.Contains("phb_")
    )
}

function Add-Line {
    param(
        [hashtable]$Summary,
        [string]$Key,
        [string]$Line
    )

    $Summary[$Key] = @($Summary[$Key]) + $Line
}

function Invoke-PowerShellLogSummary {
    param(
        [string]$ResolvedLogPath,
        [string]$ResolvedSummaryJson,
        [switch]$ShouldFailOnPhobosWarning
    )

    $lines = Get-Content -LiteralPath $ResolvedLogPath -Encoding UTF8 -ErrorAction Stop
    $timestampPattern = "^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}"
    $timestamps = @($lines | ForEach-Object {
        if ($_ -match $timestampPattern) {
            $Matches[0]
        }
    })

    $summary = [ordered]@{
        log_path = $ResolvedLogPath
        line_count = $lines.Count
        first_timestamp = $null
        last_timestamp = $null
        mod_available_lines = @()
        mod_load_lines = @()
        phobos_errors = @()
        phobos_warnings = @()
        external_errors = @()
        external_warnings = @()
    }

    if ($timestamps.Count -gt 0) {
        $summary.first_timestamp = $timestamps[0]
        $summary.last_timestamp = $timestamps[$timestamps.Count - 1]
        $start = [datetime]::ParseExact($summary.first_timestamp, "yyyy-MM-dd HH:mm:ss.fff", $null)
        $end = [datetime]::ParseExact($summary.last_timestamp, "yyyy-MM-dd HH:mm:ss.fff", $null)
        $summary.log_span_seconds = [math]::Round(($end - $start).TotalSeconds, 3)
    }

    foreach ($line in $lines) {
        if ($line.Contains("FS25_BgaExtensions") -and ($line.Contains("Available mod:") -or $line.Contains("Load mod:"))) {
            if ($line.Contains("Available mod:")) {
                Add-Line -Summary $summary -Key "mod_available_lines" -Line $line
            } else {
                Add-Line -Summary $summary -Key "mod_load_lines" -Line $line
            }
        }

        $isError = $line.Contains("Error:")
        $isWarning = $line.Contains("Warning")
        if (-not ($isError -or $isWarning)) {
            continue
        }

        $isPhobos = Test-PhobosLine -Line $line
        if ($isPhobos -and $isError) {
            Add-Line -Summary $summary -Key "phobos_errors" -Line $line
        } elseif ($isPhobos -and $isWarning) {
            Add-Line -Summary $summary -Key "phobos_warnings" -Line $line
        } elseif ($isError) {
            Add-Line -Summary $summary -Key "external_errors" -Line $line
        } else {
            Add-Line -Summary $summary -Key "external_warnings" -Line $line
        }
    }

    Write-Output "Log: $($summary.log_path)"
    Write-Output "Lines: $($summary.line_count)"
    if ($summary.first_timestamp) { Write-Output "First timestamp: $($summary.first_timestamp)" }
    if ($summary.last_timestamp) { Write-Output "Last timestamp: $($summary.last_timestamp)" }
    if ($summary.Contains("log_span_seconds")) { Write-Output "Log span: $($summary.log_span_seconds) seconds" }

    foreach ($entry in @(
        @("Mod available lines", "mod_available_lines"),
        @("Mod load lines", "mod_load_lines"),
        @("Phobos errors", "phobos_errors"),
        @("Phobos warnings", "phobos_warnings"),
        @("External errors", "external_errors"),
        @("External warnings", "external_warnings")
    )) {
        $label = $entry[0]
        $key = $entry[1]
        $values = @($summary[$key])
        Write-Output "${label}: $($values.Count)"
        foreach ($line in @($values | Select-Object -First 10)) {
            Write-Output "  $line"
        }
        if ($values.Count -gt 10) {
            Write-Output "  ... $($values.Count - 10) more"
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($ResolvedSummaryJson)) {
        $summaryDir = Split-Path -Parent $ResolvedSummaryJson
        if (-not [string]::IsNullOrWhiteSpace($summaryDir)) {
            New-Item -ItemType Directory -Force -Path $summaryDir | Out-Null
        }
        $summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ResolvedSummaryJson -Encoding UTF8
        Write-Output "Wrote $ResolvedSummaryJson"
    }

    if ($ShouldFailOnPhobosWarning -and (@($summary.phobos_errors).Count -gt 0 -or @($summary.phobos_warnings).Count -gt 0)) {
        exit 1
    }
}

function Test-CommandRuns {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        return $false
    }

    try {
        & $Command @Arguments *> $null
        return ($LASTEXITCODE -eq 0)
    } catch {
        return $false
    }
}

function Get-PythonCandidates {
    $candidates = @()

    if (-not [string]::IsNullOrWhiteSpace($env:PHOBOS_PYTHON_PATH)) {
        $candidates += [ordered]@{
            Command = $env:PHOBOS_PYTHON_PATH
            PrefixArgs = @()
            VersionArgs = @("--version")
        }
    }

    $pathCandidates = @(
        Join-Path $env:LOCALAPPDATA "Python\bin\python.exe"
        Join-Path $env:LOCALAPPDATA "Programs\Python\Python314\python.exe"
        Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"
        Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
        Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"
    )

    foreach ($path in $pathCandidates) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $candidates += [ordered]@{
                Command = $path
                PrefixArgs = @()
                VersionArgs = @("--version")
            }
        }
    }

    foreach ($commandInfo in @(Get-Command python -All -ErrorAction SilentlyContinue)) {
        $candidates += [ordered]@{
            Command = $commandInfo.Source
            PrefixArgs = @()
            VersionArgs = @("--version")
        }
    }

    foreach ($commandInfo in @(Get-Command py -All -ErrorAction SilentlyContinue)) {
        $candidates += [ordered]@{
            Command = $commandInfo.Source
            PrefixArgs = @("-3")
            VersionArgs = @("-3", "--version")
        }
    }

    $seen = @{}
    $result = @()
    foreach ($candidate in $candidates) {
        $key = "$($candidate.Command)|$($candidate.PrefixArgs -join ' ')".ToLowerInvariant()
        if ($seen.ContainsKey($key)) {
            continue
        }
        $seen[$key] = $true
        $result += $candidate
    }

    return $result
}

$pythonCommand = $null
$pythonPrefixArgs = @()

foreach ($candidate in Get-PythonCandidates) {
    if (Test-CommandRuns -Command $candidate.Command -Arguments $candidate.VersionArgs) {
        $pythonCommand = $candidate.Command
        $pythonPrefixArgs = $candidate.PrefixArgs
        break
    }
}

$measureArgs = @()

if (-not [string]::IsNullOrWhiteSpace($LogPath)) {
    $resolvedLogPath = Resolve-Path -LiteralPath $LogPath
    $measureArgs += @("--log", $resolvedLogPath.Path)
}

if (-not [string]::IsNullOrWhiteSpace($GameUserDir)) {
    $resolvedGameUserDir = Resolve-Path -LiteralPath $GameUserDir
    $measureArgs += @("--game-user-dir", $resolvedGameUserDir.Path)
}

if (-not [string]::IsNullOrWhiteSpace($SummaryJson)) {
    if ([System.IO.Path]::IsPathRooted($SummaryJson)) {
        $summaryPath = $SummaryJson
    } else {
        $summaryPath = Join-Path $repoRoot $SummaryJson
    }
    $measureArgs += @("--summary-json", $summaryPath)
}

if ($FailOnPhobosWarning) {
    $measureArgs += "--fail-on-phobos-warning"
}

if ($pythonCommand) {
    & $pythonCommand @pythonPrefixArgs $measureScript @measureArgs
    exit $LASTEXITCODE
}

Write-Output "Python 3 was not found; using the built-in PowerShell log summary."
$resolvedLog = Resolve-FS25LogPath -ExplicitLogPath $LogPath -ExplicitGameUserDir $GameUserDir
$resolvedSummary = $null
if (-not [string]::IsNullOrWhiteSpace($SummaryJson)) {
    if ([System.IO.Path]::IsPathRooted($SummaryJson)) {
        $resolvedSummary = $SummaryJson
    } else {
        $resolvedSummary = Join-Path $repoRoot $SummaryJson
    }
}
Invoke-PowerShellLogSummary -ResolvedLogPath $resolvedLog -ResolvedSummaryJson $resolvedSummary -ShouldFailOnPhobosWarning:$FailOnPhobosWarning
