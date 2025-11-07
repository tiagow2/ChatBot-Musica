# Beatfy - ChatBot de Letras de Música

O **Beatfy** é um ChatBot super simples que te ajuda a encontrar letras de músicas rapidamente. Basta dizer o nome da música e o Beatfy te traz a letra completa na hora. Ideal para quando você quer cantar junto ou está curioso sobre aquela letra que não sai da cabeça!

Com o Beatfy, nunca foi tão fácil encontrar a letra de uma música. É só digitar o nome, e o resto fica por conta do Bot.

## Funcionalidades principais:
- Encontre letras de músicas rapidamente
- Receba a letra completa só com o nome da música
- Simples, rápido e fácil de usar

Com o Beatfy, você nunca mais vai esquecer a letra da sua música favorita!

<br>

| Foto | Nome | Links |
| :---: | :---: | :---: |
| <a target="_blank" rel="noopener noreferrer" href="https://github.com/IssamiU.png?size=50"><img src="https://github.com/IssamiU.png?size=50" width="50px" style="max-width: 100%;"></a> | Issami Umeoka | <a href="https://www.linkedin.com/in/issami-umeoka-786716226/" rel="nofollow"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a> <a href="https://github.com/IssamiU"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a> |
| <a target="_blank" rel="noopener noreferrer" href="https://github.com/tiagow2.png?size=50"><img src="https://github.com/tiagow2.png?size=50" width="50px" style="max-width: 100%;"></a>| Tiago Freitas | <a href="https://www.linkedin.com/in/tiago-freitas-74730b2a9/" rel="nofollow"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a> <a href="https://github.com/tiagow2"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a> |
| <a target="_blank" rel="noopener noreferrer" href="https://github.com/nicolygz.png?size=50"><img src="https://github.com/nicolygz.png?size=50" width="50px" style="max-width: 100%;"></a> | Nicoly Guedes | <a href="https://www.linkedin.com/in/nicoly-guedes-dev/" rel="nofollow"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a> <a href="https://github.com/nicolygz"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a> |
| <a target="_blank" rel="noopener noreferrer" href="https://github.com/tuzzooz.png?size=50"><img src="https://github.com/tuzzooz.png?size=50" width="50px" style="max-width: 100%;"></a> | Otávio Vianna | <a href="https://www.linkedin.com/in/ot%C3%A1vio-vianna-lima-1b26a932a/" rel="nofollow"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a> <a href="https://github.com/tuzzooz"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a> |

## Guia rápido de instalação e execução (Windows / PowerShell)

As instruções abaixo mostram como preparar o ambiente, instalar dependências e executar os componentes principais do projeto: o servidor MCP (FastAPI), o CLI principal e o bot do Telegram (com Whisper para voz).

1) Criar e ativar um ambiente virtual (recomendado)

```powershell
# na pasta do projeto
python -m venv .venv
.\.venv\Scripts\Activate.ps1
``` 

2) Instalar dependências

```powershell
pip install --upgrade pip
pip install -r "Local AI Agent\requirements.txt"
```

Observações importantes:
- Se o pip instalou scripts em `%APPDATA%\Python\...\Scripts` e esses não estão no PATH, use o Python do venv explicitamente (como mostrado acima) ou adicione a pasta ao PATH.
- Para transcrição de voz (Whisper) é necessário ter o `ffmpeg` disponível no PATH. No Windows, baixe e extraia o ffmpeg e adicione a pasta `bin` ao PATH.
- Se você pretende usar Ollama localmente, instale e puxe um modelo compatível e configure a variável de ambiente `OLLAMA_MODEL`. Caso não use Ollama, a aplicação tem mensagens de fallback informativas.

3) Variáveis de ambiente úteis (opcional)

```powershell
# Exemplo (PowerShell)
$env:TELEGRAM_TOKEN = "<seu_telegram_token_aqui>"
$env:GENIUS_TOKEN = "<seu_genius_token_aqui>"   
# se usar integração com Genius
$env:OLLAMA_MODEL = "qwen3:4b"                
# exemplo — só se tiver o modelo local
```

4) Executar o servidor MCP (FastAPI)

Você pode executar diretamente o script ou usar o uvicorn. Se a porta 8000 estiver em uso, troque o `--port`.

```powershell
# usando uvicorn (recomendado para desenvolvimento):
python -m uvicorn "Local AI Agent.mcp_server:app" --reload --host 127.0.0.1 --port 8000

# ou, se preferir, executar o script direto (se o arquivo já chama uvicorn internamente):
python "Local AI Agent\mcp_server.py"
```

5) Executar o CLI (main.py)

```powershell
python "Local AI Agent\main.py"
```

6) Executar o bot do Telegram (opcional)

Abra outro terminal (com o venv ativado) e execute:

```powershell
python "Local AI Agent\telegram_bot.py"
```

7) Testes rápidos do MCP (Create / Read / Update / Delete)

Você pode testar os endpoints do servidor MCP manualmente com PowerShell ou automaticamente com o script de teste incluso.

-- Teste manual (PowerShell / curl)

```powershell
# Observação: o cmdlet padrão do PowerShell pode enviar o corpo como UTF-16 e
# causar erro de parsing no FastAPI. Use uma das alternativas abaixo.

# 1) PowerShell (forçar UTF-8 explicitamente) — recomendado
$json = @{ id='song-1'; title='Minha Música'; text='trecho da letra'; source='cli' } | ConvertTo-Json
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/add" -Method Post -Body $bytes -ContentType "application/json"

# LIST (GET)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/list" -Method Get

# SEARCH (POST)
$json = @{ query='trecho da letra'; k=3 } | ConvertTo-Json
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/search" -Method Post -Body $bytes -ContentType "application/json"

# UPDATE (recriar/atualizar com o mesmo id)
$json = @{ id='song-1'; title='Minha Música (v2)'; text='trecho atualizado'; source='cli' } | ConvertTo-Json
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/add" -Method Post -Body $bytes -ContentType "application/json"

# DELETE
$json = @{ id='song-1' } | ConvertTo-Json
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/delete" -Method Post -Body $bytes -ContentType "application/json"
```

Alternativa (curl.exe):

```powershell
curl.exe -X POST "http://127.0.0.1:8000/add" -H "Content-Type: application/json" -d "{\"id\":\"song-1\",\"title\":\"Minha Música\",\"text\":\"trecho da letra\",\"source\":\"cli\"}"
curl.exe "http://127.0.0.1:8000/list"
curl.exe -X POST "http://127.0.0.1:8000/search" -H "Content-Type: application/json" -d "{\"query\":\"trecho da letra\",\"k\":3}"
curl.exe -X POST "http://127.0.0.1:8000/add" -H "Content-Type: application/json" -d "{\"id\":\"song-1\",\"title\":\"Minha Música (v2)\",\"text\":\"trecho atualizado\",\"source\":\"cli\"}"
curl.exe -X POST "http://127.0.0.1:8000/delete" -H "Content-Type: application/json" -d "{\"id\":\"song-1\"}"
```

- Teste automático com Python (script incluído):

Salve e execute o script de teste que acompanha este repositório:

```powershell
python "Local AI Agent\test_mcp.py"
```

O script `test_mcp.py` executa sequencialmente: CREATE -> LIST -> SEARCH -> UPDATE -> DELETE e imprime resultados.

## Dicas de depuração e problemas comuns
- Erro ao bind na porta 8000 (WinError 10048): verifique se outro processo já usa a porta. Para listar processos no Windows use `netstat -ano | Select-String ":8000"` e mate o PID com `Stop-Process -Id <PID>` ou mude o `--port` do uvicorn.
- Se o LLM (Ollama) retornar erro de modelo não encontrado, defina `OLLAMA_MODEL` para um modelo que esteja instalado localmente ou use o fallback informativo. Outra opção é configurar uma integração com OpenAI (não implementada automaticamente ainda).
- Whisper/ffmpeg: se a transcrição de voz falhar, verifique se `ffmpeg` está acessível no PATH.

## Arquivos úteis
- `Local AI Agent/mcp_server.py` — servidor FastAPI que persiste documentos e embeddings em SQLite e expõe endpoints REST.
- `Local AI Agent/main.py` — CLI principal que busca letras, indexa no MCP (ou LocalAgent como fallback) e consulta o LLM.
- `Local AI Agent/telegram_bot.py` — bot do Telegram que aceita mensagens de texto e voz (Whisper).
- `Local AI Agent/test_mcp.py` — script de teste para os endpoints MCP (CREATE/READ/UPDATE/DELETE).

