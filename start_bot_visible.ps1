<#
start_bot_visible.ps1
Inicia o bot do Telegram em uma janela visível para debug.
Uso: .\start_bot_visible.ps1
#>

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Iniciando bot do Telegram (janela visível) ===" -ForegroundColor Cyan

# Token do bot
$token = "8546795451:AAEk--x1uayt7YLdFRvx7KPmmGGsUTsj6tw"

Write-Host "Aguarde o carregamento das dependências (torch, transformers)..." -ForegroundColor Yellow
Write-Host "Isso pode demorar 10-30 segundos na primeira execução." -ForegroundColor Yellow
Write-Host ""

# Executar bot no terminal atual
$env:TELEGRAM_TOKEN = $token
& "$scriptDir\.venv\Scripts\python.exe" "$scriptDir\Local AI Agent\telegram_bot.py"
