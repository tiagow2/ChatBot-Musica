<#
Start helper for Telegram bot.
Usage:
  # Prompt for token interactively
  .\start_bot.ps1

  # Or pass token as parameter (recommended if running from automation)
  .\start_bot.ps1 -Token "8537677004:AAGJa2-qMETZ4zqvDkyWm03sAQGBGjvb10s"

This script does NOT save the token to disk. It sets the TELEGRAM_TOKEN only for the process that runs the bot.
Do NOT commit secrets to source control. Add tokens to your environment or a local-only .env if needed.
#>
param(
    [string]$Token
)

# Ensure script runs from repo root (where this script is located)
Set-Location -Path $PSScriptRoot

# Activate venv if exists
if (Test-Path "..\.venv\Scripts\Activate.ps1") {
    Write-Host "Ativando venv..."
    . "..\.venv\Scripts\Activate.ps1"
} elseif (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "Ativando venv..."
    . ".\.venv\Scripts\Activate.ps1"
} else {
    Write-Warning "Não encontrei um venv em .venv. Certifique-se de ter criado e ativado o ambiente virtual manualmente se necessário."
}

if (-not $Token) {
    $Token = Read-Host -Prompt "8537677004:AAGJa2-qMETZ4zqvDkyWm03sAQGBGjvb10s"
}

if (-not $Token) {
    Write-Error "Nenhum token fornecido. Saindo."
    exit 1
}

# Set token for this process only
$env:TELEGRAM_TOKEN = $Token

Write-Host "Iniciando telegram_bot.py com token fornecido (não salvo em disco) ..."
python "Local AI Agent\telegram_bot.py"
