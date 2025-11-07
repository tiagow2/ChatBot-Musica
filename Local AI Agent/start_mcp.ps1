<#
start_mcp.ps1

Ativa o venv (se existir) e inicia o servidor MCP (uvicorn) na porta 8000.
Uso:
  .\start_mcp.ps1

Observação: deixe este terminal aberto enquanto testar endpoints.
#>

Write-Host "== start_mcp.ps1 =="

# tentar ativar venv relativo ao repositório
if (Test-Path "..\.venv\Scripts\Activate.ps1") {
    Write-Host "Ativando venv ..\.venv\Scripts\Activate.ps1"
    . "..\.venv\Scripts\Activate.ps1"
} elseif (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "Ativando venv .\.venv\Scripts\Activate.ps1"
    . ".\.venv\Scripts\Activate.ps1"
} else {
    Write-Warning "Não encontrei .venv automaticamente. Garanta que o ambiente virtual esteja ativado manualmente se necessário."
}

Write-Host "Iniciando MCP server (uvicorn) em http://127.0.0.1:8000"
python -m uvicorn "Local AI Agent.mcp_server:app" --host 127.0.0.1 --port 8000
