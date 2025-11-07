<#
start_bot_debug.ps1

Ativa o venv (se existir) e inicia o bot Telegram redirecionando saída para um arquivo de log.
Uso:
    .\start_bot_debug.ps1
    .\start_bot_debug.ps1 -Token "<seu_token>"

O script pergunta pelo token se não fornecido; o token não é salvo em disco e é definido apenas para a sessão do processo.

Logs são escritos em Local AI Agent/logs/telegram_bot.log
#>

param(
    [string]$Token
)

$logdir = Join-Path -Path $PSScriptRoot -ChildPath 'logs'
if (-not (Test-Path $logdir)) { New-Item -ItemType Directory -Path $logdir | Out-Null }
$logfile = Join-Path -Path $logdir -ChildPath 'telegram_bot.log'

# ativar venv relativo
if (Test-Path "..\.venv\Scripts\Activate.ps1") {
    . "..\.venv\Scripts\Activate.ps1"
} elseif (Test-Path ".\.venv\Scripts\Activate.ps1") {
    . ".\.venv\Scripts\Activate.ps1"
} else {
    Write-Warning "Não encontrei .venv automaticamente. Garanta que o ambiente virtual esteja ativado manualmente se necessário."
}

if (-not $Token) {
    $Token = Read-Host -Prompt "Cole o TELEGRAM_TOKEN do BotFather (não será salvo em disco)"
}

if (-not $Token) {
    Write-Error "Nenhum token fornecido. Saindo."
    exit 1
}

# definir token apenas para a sessão do processo
$env:TELEGRAM_TOKEN = $Token

Write-Host "Iniciando telegram_bot.py - logs em: $logfile"
# roda e grava stdout/stderr no logfile
python ".\Local AI Agent\telegram_bot.py" *> $logfile

Write-Host "telegram_bot.py finalizado. Ver logs em: $logfile"
