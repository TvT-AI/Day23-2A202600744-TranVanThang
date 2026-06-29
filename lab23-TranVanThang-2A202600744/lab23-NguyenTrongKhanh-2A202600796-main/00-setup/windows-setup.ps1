## Windows pre-flight check (PowerShell).
## Run via: pwsh windows-setup.ps1
## Or:      powershell -ExecutionPolicy Bypass -File windows-setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "Checking Windows lab prerequisites..."

# WSL2?
$wsl = wsl --status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: WSL not installed. Run in admin PowerShell:" -ForegroundColor Red
    Write-Host "  wsl --install"
    exit 1
}

# Docker Desktop?
$docker = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $docker) {
    Write-Host "ERROR: Docker Desktop not running. Start it from the Start menu." -ForegroundColor Red
    exit 1
}

# Docker daemon reachable?
docker version --format '{{.Server.Version}}' | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker daemon not reachable." -ForegroundColor Red
    Write-Host "  Toggle Docker Desktop's WSL2 integration in: Settings > Resources > WSL Integration"
    exit 1
}

# Compose v2?
docker compose version --short | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Compose v2 missing. Reinstall Docker Desktop (latest version)." -ForegroundColor Red
    exit 1
}

Write-Host "Windows setup OK." -ForegroundColor Green
Write-Host "TIP: run 'make' commands from a WSL2 shell, not PowerShell." -ForegroundColor Yellow
