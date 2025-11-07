<#
start_services.ps1
Inicia o servidor MCP e o bot do Telegram em processos separados.
Uso: .\start_services.ps1 -TelegramToken "<seu_token>"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$TelegramToken
)

$scriptDir = $PSScriptRoot

Write-Host "=== Iniciando serviços do ChatBot-Musica ===" -ForegroundColor Cyan

# Ativar venv se existir
if (Test-Path "$scriptDir\.venv\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
    & "$scriptDir\.venv\Scripts\Activate.ps1"
}

# Iniciar servidor MCP em background
Write-Host "Iniciando servidor MCP (FastAPI)..." -ForegroundColor Green
$mcpProcess = Start-Process -FilePath "$scriptDir\.venv\Scripts\python.exe" `
    -ArgumentList "-m", "uvicorn", "Local AI Agent.mcp_server:app", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory $scriptDir `
    -PassThru `
    -WindowStyle Hidden

Write-Host "Servidor MCP iniciado (PID: $($mcpProcess.Id))" -ForegroundColor Green
Start-Sleep -Seconds 3

# Iniciar bot do Telegram em background
Write-Host "Iniciando bot do Telegram..." -ForegroundColor Green
$env:TELEGRAM_TOKEN = $TelegramToken

$botProcess = Start-Process -FilePath "$scriptDir\.venv\Scripts\python.exe" `
    -ArgumentList "$scriptDir\Local AI Agent\telegram_bot.py" `
    -WorkingDirectory $scriptDir `
    -PassThru `
    -WindowStyle Hidden `
    -Environment @{TELEGRAM_TOKEN=$TelegramToken}

Write-Host "Bot do Telegram iniciado (PID: $($botProcess.Id))" -ForegroundColor Green
Write-Host ""
Write-Host "=== Serviços rodando ===" -ForegroundColor Cyan
Write-Host "  - Servidor MCP: http://127.0.0.1:8000 (PID: $($mcpProcess.Id))"
Write-Host "  - Bot Telegram: PID $($botProcess.Id)"
Write-Host ""
Write-Host "Para parar os serviços:" -ForegroundColor Yellow
Write-Host "  Get-Process python | Stop-Process -Force"
Write-Host ""
Write-Host "Logs em tempo real (escolha um PID):"
Write-Host "  Get-Process -Id <PID> | Format-List *"
