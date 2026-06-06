param(
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$modRoot = Join-Path $repoRoot "mod"

if (-not (Test-Path -LiteralPath $modRoot -PathType Container)) {
    throw "Mod source folder not found: $modRoot"
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $distRoot = Join-Path $repoRoot "dist"
    $OutputPath = Join-Path $distRoot "FS25_BgaExtensions.zip"
}

$resolvedOutputParent = Split-Path -Parent $OutputPath
if ([string]::IsNullOrWhiteSpace($resolvedOutputParent)) {
    $resolvedOutputParent = Get-Location
}

New-Item -ItemType Directory -Force -Path $resolvedOutputParent | Out-Null

if (Test-Path -LiteralPath $OutputPath) {
    Remove-Item -LiteralPath $OutputPath -Force
}

$items = Get-ChildItem -LiteralPath $modRoot -Force
Compress-Archive -LiteralPath $items.FullName -DestinationPath $OutputPath -CompressionLevel Optimal

Write-Output "Created $OutputPath"
