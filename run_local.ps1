#!/usr/bin/env pwsh
# run_local.ps1
# Script to run the Multi-Agent Productivity Assistant locally without Docker
$ErrorActionPreference = "Stop"

Write-Host "Starting Multi-Agent Productivity Assistant (Local Mode without Docker)" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor Cyan

# Define background processes list
$script:pidsToKill = @()

# Cleanup function to kill background processes on exit
Function Cleanup {
    Write-Host "`nStopping all background processes..." -ForegroundColor Yellow
    foreach ($pid_to_kill in $script:pidsToKill) {
        try {
            Stop-Process -Id $pid_to_kill -Force -ErrorAction SilentlyContinue
        }
        catch { }
    }
    Write-Host "All processes stopped. Goodbye!" -ForegroundColor Green
    Exit 0
}

# We will handle cleanup through a try-finally block below instead of event hooks

# Ensure we're in the right directory
$RootDir = $PSScriptRoot
Set-Location $RootDir

# Automatically activate virtual environment if it exists
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "⚡ Activating virtual environment..." -ForegroundColor Cyan
    . .\.venv\Scripts\Activate.ps1
}
elseif (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "⚡ Activating virtual environment..." -ForegroundColor Cyan
    . .\venv\Scripts\Activate.ps1
}

# Set Environment Variables needed for Orchestrator to find MCP Servers
$env:FIRESTORE_MODE = "mock"
$env:PYTHONPATH = $RootDir
$env:PORT = "8000"
$env:MCP_TASK_HOST = "localhost"
$env:MCP_TASK_PORT = "8001"
$env:MCP_CALENDAR_HOST = "localhost"
$env:MCP_CALENDAR_PORT = "8002"
$env:MCP_NOTES_HOST = "localhost"
$env:MCP_NOTES_PORT = "8003"
$env:MCP_CRITIC_HOST = "localhost"
$env:MCP_CRITIC_PORT = "8004"
$env:MCP_AUDITOR_HOST = "localhost"
$env:MCP_AUDITOR_PORT = "8005"
$env:MCP_EVENT_MONITOR_HOST = "localhost"
$env:MCP_EVENT_MONITOR_PORT = "8006"
$env:MCP_RESEARCH_HOST = "localhost"
$env:MCP_RESEARCH_PORT = "8007"
$env:MCP_NEWS_HOST = "localhost"
$env:MCP_NEWS_PORT = "8008"

# 1. Start MCP Servers in background
Write-Host "Starting MCP Servers..." -ForegroundColor Yellow

$mcp_servers = @(
    @{ Name = "task"; Port = 8001 },
    @{ Name = "calendar"; Port = 8002 },
    @{ Name = "notes"; Port = 8003 },
    @{ Name = "critic"; Port = 8004 },
    @{ Name = "auditor"; Port = 8005 },
    @{ Name = "event_monitor"; Port = 8006 },
    @{ Name = "research"; Port = 8007 },
    @{ Name = "news"; Port = 8008 }
)

foreach ($server in $mcp_servers) {
    # Using python -m uvicorn instead of directly so we can set env inline if needed,
    # but env vars are inherited
    $env:MCP_SERVER = $server.Name
    $env:MCP_PORT = $server.Port
    
    $proc = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "backend.mcp_tools.server:app", "--host", "127.0.0.1", "--port", $server.Port -WindowStyle Minimized -PassThru
    $script:pidsToKill += $proc.Id
    Write-Host "   Started $($server.Name) on port $($server.Port) (PID: $($proc.Id))" -ForegroundColor Green
}

try {
    # 2. Start the main FastAPI Orchestrator App in foreground
    Write-Host "Starting Orchestrator API and Dashboard on http://localhost:8000" -ForegroundColor Magenta
    Write-Host "Press Ctrl+C to stop everything." -ForegroundColor Gray
    Write-Host "==========================================================================" -ForegroundColor Cyan

    Remove-Item Env:\MCP_PORT -ErrorAction SilentlyContinue

    python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
} finally {
    # If uvicorn crashes or user stops it:
    Cleanup
}
