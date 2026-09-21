[CmdletBinding()]
param(
    [string]$KimiPath,
    [string]$ModelAlias = 'kimi-code/k3',
    [switch]$Check
)

$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$taskSkills = Join-Path $PSScriptRoot 'skills'

if (-not $KimiPath) {
    $taskCommand = Get-Command kimi -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($taskCommand) { $KimiPath = $taskCommand.Source }
    else { $KimiPath = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.kimi-code\bin\kimi.exe' }
}
if (-not (Test-Path -LiteralPath $KimiPath -PathType Leaf)) {
    throw 'Kimi Code is not installed at the selected path. Install/sign in before the demo; this script does not install it.'
}
$KimiPath = (Resolve-Path -LiteralPath $KimiPath).Path
$taskVersion = ((& $KimiPath --version) | Out-String).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Cannot read the Kimi Code version.' }
$taskHelp = ((& $KimiPath --help) | Out-String)
if ($LASTEXITCODE -ne 0 -or $taskHelp -notmatch '--skills-dir' -or $taskHelp -notmatch '--model') {
    throw 'This launcher needs Kimi Code with native --skills-dir and --model support.'
}

$taskDataRoot = $env:KIMI_CODE_HOME
if (-not $taskDataRoot) { $taskDataRoot = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.kimi-code' }
$taskConfig = Join-Path $taskDataRoot 'config.toml'
if (-not (Test-Path -LiteralPath $taskConfig -PathType Leaf)) {
    throw 'Kimi Code configuration is missing. Sign in/configure K3 before the demo.'
}

# Read only the selected model table. Do not print provider fields or credentials.
# This accepts the quoted model-table form written by Kimi and shown in its docs.
$taskTable = ''
$taskRawModel = $null
foreach ($taskLine in [System.IO.File]::ReadLines($taskConfig)) {
    if ($taskLine -match '^\s*\[models\."([^"\r\n]+)"\]\s*(?:#.*)?$') { $taskTable = $Matches[1]; continue }
    if ($taskLine -match "^\s*\[models\.'([^'\r\n]+)'\]\s*(?:#.*)?$") { $taskTable = $Matches[1]; continue }
    if ($taskLine -match '^\s*\[') { $taskTable = ''; continue }
    if ($taskTable -ceq $ModelAlias -and $taskLine -match '^\s*model\s*=\s*"([^"\r\n]+)"\s*(?:#.*)?$') { $taskRawModel = $Matches[1] }
    if ($taskTable -ceq $ModelAlias -and $taskLine -match "^\s*model\s*=\s*'([^'\r\n]+)'\s*(?:#.*)?$") { $taskRawModel = $Matches[1] }
}
if ($taskRawModel -notin @('k3', 'k3-256k', 'kimi-k3')) {
    throw "The selected alias '$ModelAlias' is missing or does not map to a recognized K3 model. Configure K3 explicitly; no fallback model will be used."
}

$taskArguments = @('--model', $ModelAlias, '--skills-dir', $taskSkills)
if ($Check) {
    [pscustomobject]@{
        status = 'K3_ALIAS_AND_FLAGS_CHECKED'
        executable = $KimiPath
        version = $taskVersion
        model_alias = $ModelAlias
        model_id = $taskRawModel
        working_directory = $taskRoot
        arguments = $taskArguments
        model_request_made = $false
        config_parse_validated = $false
        authentication_checked = $false
        deck_tools_qualified = $false
    } | ConvertTo-Json -Depth 4
    return
}

Write-Host "Kimi Code $taskVersion | $ModelAlias ($taskRawModel)"
Write-Host 'Choose: /skill:demo-slides, /skill:create-slides or /skill:improve-slides, followed by your files and brief.'
Write-Host 'Prepared demo: /skill:demo-slides Use example_input/inventories-hkas2-knowledge.md to create 6 slides.'
Push-Location -LiteralPath $taskRoot
try {
    # Array splatting preserves paths as arguments. Never evaluate user text as shell code.
    & $KimiPath @taskArguments
    if ($LASTEXITCODE -ne 0) { throw "Kimi Code exited with code $LASTEXITCODE." }
}
finally { Pop-Location }
