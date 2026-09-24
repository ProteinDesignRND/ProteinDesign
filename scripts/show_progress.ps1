<#
.SYNOPSIS
    Shows current progress state of the Protein Design project.
.DESCRIPTION
    Reads reports/AG_RUN_STATE.json and displays a formatted summary.
    Run from the project root directory.
.EXAMPLE
    .\scripts\show_progress.ps1
#>

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$stateFile = Join-Path (Join-Path $projectRoot "reports") "AG_RUN_STATE.json"

if (-not (Test-Path $stateFile)) {
    Write-Host "No progress state found at: $stateFile" -ForegroundColor Yellow
    Write-Host "The AI agent has not started or has not created the progress file yet."
    exit 0
}

$state = Get-Content $stateFile -Raw | ConvertFrom-Json

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " PROTEIN DESIGN - Progress Report" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$stateColor = "White"
if ($state.state -eq "RUNNING") { $stateColor = "Green" }
elseif ($state.state -eq "PLANNING") { $stateColor = "Yellow" }
elseif ($state.state -eq "WAITING") { $stateColor = "Yellow" }
elseif ($state.state -eq "BLOCKED") { $stateColor = "Red" }
elseif ($state.state -eq "DONE" -or $state.state -eq "COMPLETE") { $stateColor = "Cyan" }

Write-Host "  State:           " -NoNewline
Write-Host $state.state -ForegroundColor $stateColor

Write-Host "  Current Stage:   $($state.current_stage)"
Write-Host "  Started:         $($state.start_time)"
Write-Host "  Last Update:     $($state.last_update)"

if ($state.expected_remaining_minutes) {
    Write-Host "  Est. Remaining:  ~$($state.expected_remaining_minutes) minutes"
}

Write-Host ""
Write-Host "  Completed:" -ForegroundColor Green
foreach ($item in $state.completed) {
    Write-Host "    [x] $item"
}

Write-Host ""
Write-Host "  In Progress:" -ForegroundColor Yellow
foreach ($item in $state.in_progress) {
    Write-Host "    [ ] $item"
}

if ($state.blocked -and $state.blocked.Count -gt 0) {
    Write-Host ""
    Write-Host "  Blocked:" -ForegroundColor Red
    foreach ($item in $state.blocked) {
        Write-Host "    [!] $item"
    }
}

Write-Host ""
Write-Host "  Next Action:     $($state.next_action)"
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan

# Git status summary
Write-Host ""
Write-Host "  Git Branch:" -NoNewline
$branch = git -C $projectRoot branch --show-current 2>$null
Write-Host " $branch" -ForegroundColor Cyan

$gitStatus = git -C $projectRoot status --short 2>$null
$modCount = 0
$untrackedCount = 0
if ($gitStatus) {
    foreach ($line in $gitStatus) {
        if ($line -match "^ M") { $modCount++ }
        if ($line -match "^\?\?") { $untrackedCount++ }
    }
}
Write-Host "  Modified files:  $modCount"
Write-Host "  Untracked files: $untrackedCount"

# Check historical repo
$histPath = Join-Path (Join-Path $projectRoot "external") "proteinsolver-original"
$histStatus = git -C $histPath status --short 2>$null
if ([string]::IsNullOrWhiteSpace($histStatus)) {
    Write-Host "  Historical repo:  " -NoNewline
    Write-Host "CLEAN" -ForegroundColor Green
} else {
    Write-Host "  Historical repo:  " -NoNewline
    Write-Host "MODIFIED (WARNING)" -ForegroundColor Red
}

Write-Host ""
