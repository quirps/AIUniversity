param(
    [string]$Model = "anthropic/claude-opus-5.5",
    [int]$MaxTokens = 64000,
    [string]$ReasoningEffort = "low",
    [double]$Temperature = 0.2,
    [string]$UserPromptPath = "",
    [string]$SystemPromptPath = ""
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Repair-Mojibake([string]$s) {
    if ([string]::IsNullOrEmpty($s)) { return $s }
    if ($s -notmatch '[\u00C2\u00C3\u00E2]') { return $s }
    $latin1 = [System.Text.Encoding]::GetEncoding(28591)
    return [System.Text.Encoding]::UTF8.GetString($latin1.GetBytes($s))
}

$root = Split-Path -Parent $PSScriptRoot
$kickoffPath = Join-Path $root "ops\OPUS_KICKOFF.md"
$sourcePath = Join-Path $root "source\concept_map.txt"

if (-not $env:OPENROUTER_API_KEY) { throw "OPENROUTER_API_KEY is not set in the process environment." }
foreach ($p in @($kickoffPath, $sourcePath)) { if (-not (Test-Path $p)) { throw "Missing required file: $p" } }

if ($SystemPromptPath) {
    if (-not (Test-Path $SystemPromptPath)) { throw "Missing system prompt file: $SystemPromptPath" }
    $system = [System.IO.File]::ReadAllText($SystemPromptPath, [System.Text.Encoding]::UTF8)
} else {
    $system = [System.IO.File]::ReadAllText($kickoffPath, [System.Text.Encoding]::UTF8)
}
$source = [System.IO.File]::ReadAllText($sourcePath, [System.Text.Encoding]::UTF8)

if ($UserPromptPath) {
    if (-not (Test-Path $UserPromptPath)) { throw "Missing user prompt file: $UserPromptPath" }
    $user = [System.IO.File]::ReadAllText($UserPromptPath, [System.Text.Encoding]::UTF8)
} else {
$user = @"
The full source concept map follows between the markers.

<source>
$source
</source>

Hardware and transparency constraints are already in your system prompt. Apply them explicitly, especially the hardware_tier requirement and the in-repo learning log.

Produce every deliverable listed in section 9 now.

Response format:
- For each file, emit a heading line exactly in the form: ## FILE: <path>
- Follow it with one fenced code block containing the exact file contents.
- Put all open decisions at the very end under "## OPEN DECISIONS".
- No commentary outside those sections.
- Do not abbreviate schemas or tickets. TRACEABILITY.md may use one row per source bullet, not per sentence.
- Keep prose tight and contractual. Prefer exact commands, types, and thresholds over explanation.
"@
}

$body = @{
    model = $Model
    messages = @(
        @{ role = "system"; content = $system },
        @{ role = "user"; content = $user }
    )
    temperature = $Temperature
    max_tokens = $MaxTokens
    reasoning = @{
        effort = $ReasoningEffort
        exclude = $true
    }
} | ConvertTo-Json -Depth 20 -Compress

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outDir = Join-Path $root "ops\opus\$stamp"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

$headers = @{
    "Authorization" = "Bearer $($env:OPENROUTER_API_KEY)"
    "HTTP-Referer" = "https://github.com/local/AIUniversity"
    "X-Title" = "AI University Architect Call"
}

$meta = [ordered]@{
    timestamp = (Get-Date).ToString("o")
    model = $Model
    temperature = $Temperature
    max_tokens = $MaxTokens
    reasoning_effort = $ReasoningEffort
    kickoff_chars = $system.Length
    source_chars = $source.Length
    prompt_chars = $system.Length + $user.Length
    response_dir = $outDir
}

try {
    $resp = Invoke-RestMethod -Uri "https://openrouter.ai/api/v1/chat/completions" `
        -Method Post `
        -Headers $headers `
        -ContentType "application/json; charset=utf-8" `
        -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) `
        -TimeoutSec 900

    $resp | ConvertTo-Json -Depth 50 | Set-Content -Path (Join-Path $outDir "response.json") -Encoding UTF8

    $content = $resp.choices[0].message.content
    if ($null -eq $content) { $content = "" }
    if ($content -is [System.Array]) {
        $parts = foreach ($block in $content) {
            if ($block.text) { $block.text }
            elseif ($block.type) { "[$($block.type) block omitted]" }
        }
        $content = ($parts -join "`n")
    }
    $content = Repair-Mojibake $content
    $content | Set-Content -Path (Join-Path $outDir "response.md") -Encoding UTF8

    if ($resp.choices[0].message.reasoning) {
        (Repair-Mojibake $resp.choices[0].message.reasoning) | Set-Content -Path (Join-Path $outDir "reasoning.md") -Encoding UTF8
    }

    $meta["finish_reason"] = $resp.choices[0].finish_reason
    $meta["usage"] = $resp.usage
    $meta["response_chars"] = $content.Length
    $meta | ConvertTo-Json -Depth 10 | Set-Content -Path (Join-Path $outDir "meta.json") -Encoding UTF8

    Write-Output "OK $outDir"
    Write-Output "finish_reason=$($resp.choices[0].finish_reason) chars=$($content.Length)"
}
catch {
    $err = $_.Exception.Message
    $meta["error"] = $err
    $meta | ConvertTo-Json -Depth 10 | Set-Content -Path (Join-Path $outDir "meta.json") -Encoding UTF8
    if ($_.ErrorDetails.Message) {
        $_.ErrorDetails.Message | Set-Content -Path (Join-Path $outDir "error.json") -Encoding UTF8
    }
    throw
}
