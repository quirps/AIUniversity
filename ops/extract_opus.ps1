param(
    [Parameter(Mandatory = $true)][string]$ResponsePath,
    [string]$OutRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $OutRoot) { $OutRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }
$text = [System.IO.File]::ReadAllText($ResponsePath, [System.Text.Encoding]::UTF8)

if ($text -match '[\u00C2\u00C3\u00E2]') {
    $latin1 = [System.Text.Encoding]::GetEncoding(28591)
    $text = [System.Text.Encoding]::UTF8.GetString($latin1.GetBytes($text))
}

$pattern = '(?m)^## FILE:\s*(.+?)\s*$'
$fileMatches = [regex]::Matches($text, $pattern)
if ($fileMatches.Count -eq 0) { throw "No '## FILE:' headings found in $ResponsePath" }

$utf8 = New-Object System.Text.UTF8Encoding($false)
$written = @()

for ($i = 0; $i -lt $fileMatches.Count; $i++) {
    $rel = $fileMatches[$i].Groups[1].Value.Trim()
    if ($rel -match '^[A-Za-z]:' -or $rel -match '(^|[\\/])\.\.([\\/]|$)' -or $rel.StartsWith('/') -or $rel.StartsWith('\')) {
        throw "Refusing unsafe path: $rel"
    }
    $start = $fileMatches[$i].Index + $fileMatches[$i].Length
    $end = if ($i + 1 -lt $fileMatches.Count) { $fileMatches[$i + 1].Index } else { $text.Length }
    $body = $text.Substring($start, $end - $start).Trim()

    $lines = $body -split "`r?`n"
    if ($lines.Count -gt 0 -and $lines[0] -match '^```') {
        $lines = $lines[1..($lines.Count - 1)]
    }
    if ($lines.Count -gt 0 -and $lines[$lines.Count - 1] -match '^```\s*$') {
        $lines = $lines[0..($lines.Count - 2)]
    }
    $content = ($lines -join "`n").TrimEnd() + "`n"

    $target = Join-Path $OutRoot $rel
    $dir = Split-Path -Parent $target
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    [System.IO.File]::WriteAllText($target, $content, $utf8)
    $written += [pscustomobject]@{ Path = $rel; Chars = $content.Length; Closed = ($body.TrimEnd().EndsWith('```')) }
}

$written | Format-Table -AutoSize
"Extracted $($written.Count) file(s) to $OutRoot"
