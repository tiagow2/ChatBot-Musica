<#
keep_bot_alive.ps1
Mantém o bot rodando, reiniciando automaticamente se cair.
Execute este script antes da apresentação e deixe rodando.
#>

$token = "8546795451:AAEk--x1uayt7YLdFRvx7KPmmGGsUTsj6tw"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Monitor do Bot do Telegram ===" -ForegroundColor Cyan
Write-Host "Mantendo o bot ativo. Pressione Ctrl+C para parar." -ForegroundColor Yellow
Write-Host ""

while ($true) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Iniciando bot..." -ForegroundColor Green
    
    $env:TELEGRAM_TOKEN = $token
    
    # Executa o bot e captura o código de saída
    & "$scriptDir\.venv\Scripts\python.exe" "$scriptDir\Local AI Agent\telegram_bot.py"
    
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Bot encerrado normalmente." -ForegroundColor Yellow
    } else {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Bot crashou (código: $exitCode). Reiniciando em 5s..." -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 5
}
