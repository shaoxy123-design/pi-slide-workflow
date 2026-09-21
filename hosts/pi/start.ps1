[CmdletBinding()]
param(
    [string]$PiPath,
    [string]$PiPackagePath,
    [string]$Provider = 'zai',
    [ValidateSet('glm-5.3-flash', 'glm-5.3')][string]$MainModel = 'glm-5.3-flash',
    [ValidateSet('low', 'high', 'max')][string]$Thinking = 'high',
    [switch]$Check
)

$ErrorActionPreference = 'Stop'
$slideRepo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
if (-not $PiPath) {
    $slidePiCommand = Get-Command pi -CommandType ExternalScript,Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $slidePiCommand) { throw 'Install Pi and configure your GLM provider before using this launcher.' }
    $PiPath = $slidePiCommand.Source
}
$PiPath = (Resolve-Path -LiteralPath $PiPath).Path
if (-not $PiPackagePath) {
    $PiPackagePath = Join-Path (Split-Path -Parent $PiPath) 'node_modules\@earendil-works\pi-coding-agent'
}
if (-not (Test-Path -LiteralPath (Join-Path $PiPackagePath 'package.json') -PathType Leaf)) {
    throw 'Cannot locate the Pi npm package. Supply -PiPackagePath with its installed directory; this launcher does not install or update Pi.'
}
$PiPackagePath = (Resolve-Path -LiteralPath $PiPackagePath).Path
$slideNode = Get-Command node -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $slideNode) { throw 'Node.js is needed for the installed Pi package and offline preflight.' }

# Inspect the installed runtime/catalog without invoking a model or reading keys.
& $slideNode.Source (Join-Path $PSScriptRoot 'check.mjs') --pi-package $PiPackagePath --provider $Provider --main-model $MainModel --thinking $Thinking
if ($LASTEXITCODE -ne 0) { throw 'Pi preflight did not pass. Resolve the reported model/runtime gap before launching; no fallback model was selected.' }
if ($Check) { return }

$slideArgs = @('--provider', $Provider, '--model', $MainModel, '--thinking', $Thinking,
    '--no-extensions', '-e', (Join-Path $PSScriptRoot 'extension.ts'),
    '--no-skills', '--skill', (Join-Path $PSScriptRoot 'skills'), '--no-prompt-templates')
Write-Host "Planner/content: $MainModel | Visual workers: glm-5.3-flash | exactly three logical roles"
Write-Host '/skill:demo-slides Use example_input/inventories-hkas2-knowledge.md to create 6 slides.'
Push-Location -LiteralPath $slideRepo
try {
    & $PiPath @slideArgs
    if ($LASTEXITCODE -ne 0) { throw "Pi exited with code $LASTEXITCODE." }
}
finally { Pop-Location }
