# run_all.ps1
# Script completo que inicia servidor MCP + bot do Telegram

$token = "8546795451:AAEk--x1uayt7YLdFRvx7KPmmGGsUTsj6tw"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== ChatBot-Musica - Inicializador Completo ===" -ForegroundColor Cyan
Write-Host ""

# Ativar venv
if (Test-Path "$scriptDir\.venv\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
    & "$scriptDir\.venv\Scripts\Activate.ps1"
} else {
    Write-Host "ERRO: .venv nao encontrado!" -ForegroundColor Red
    exit 1
}

# Iniciar servidor MCP
Write-Host "[1/2] Iniciando servidor MCP..." -ForegroundColor Green
$mcpJob = Start-Job -ScriptBlock {
    param($venvPath, $workDir)
    Set-Location $workDir
    & "$venvPath\Scripts\python.exe" -m uvicorn "Local AI Agent.mcp_server:app" --host 127.0.0.1 --port 8000
} -ArgumentList "$scriptDir\.venv", $scriptDir

Start-Sleep -Seconds 3
Write-Host "Servidor MCP iniciado!" -ForegroundColor Green

# Iniciar bot
Write-Host "[2/2] Iniciando bot do Telegram..." -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar." -ForegroundColor Yellow
Write-Host ""

$env:TELEGRAM_TOKEN = $token
$botRestartCount = 0

while ($true) {
    $tentativa = $botRestartCount + 1
    Write-Host "Bot iniciando... (tentativa $tentativa)" -ForegroundColor Cyan
    
    & "$scriptDir\.venv\Scripts\python.exe" "$scriptDir\Local AI Agent\telegram_bot.py"
    
    $exitCode = $LASTEXITCODE
    $botRestartCount = $botRestartCount + 1
    
    if ($exitCode -eq 0) {
        Write-Host "Bot encerrado normalmente." -ForegroundColor Yellow
    } else {
        Write-Host "Bot crashou. Reiniciando em 5s..." -ForegroundColor Red
    }
    
    # Checar servidor MCP
    $mcpStatus = Get-Job -Id $mcpJob.Id -ErrorAction SilentlyContinue
    if ($mcpStatus.State -ne "Running") {
        Write-Host "Servidor MCP parou! Reiniciando..." -ForegroundColor Yellow
        $mcpJob = Start-Job -ScriptBlock {
            param($venvPath, $workDir)
            Set-Location $workDir
            & "$venvPath\Scripts\python.exe" -m uvicorn "Local AI Agent.mcp_server:app" --host 127.0.0.1 --port 8000
        } -ArgumentList "$scriptDir\.venv", $scriptDir
    }
    
    Start-Sleep -Seconds 5
}
