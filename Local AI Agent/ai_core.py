import os
import time
import lyricsgenius
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from local_agent import LocalAgent
import httpx
from langchain_core.prompts import PromptTemplate

# Token Genius (mantenha seguro em variáveis de ambiente em produção)
GENIUS_TOKEN = os.environ.get("GENIUS_TOKEN", "x5lnU50yJ34O0nmdOD9NszzrxXl8iz-d_9F8yr1JmSJ7z2MaglqCYwh7gztl1_pW")

genius = lyricsgenius.Genius(GENIUS_TOKEN, timeout=30)

template = """
Você é um expert de letras de música, sempre responda em português do Brasil. Você sabe todas as letras de todas as músicas e devolve as letras das músicas com base no título.


Aqui está a letra da música:
{reviews}

Aqui está o título da música para responder:
{question}
"""

prompt = ChatPromptTemplate.from_template(template)
# Modelo Ollama configurável via variável de ambiente OLLAMA_MODEL.
# Por padrão tentamos 'qwen3:4b', mas se o modelo não estiver instalado
# você pode definir OLLAMA_MODEL para o nome listado por `ollama list`,
# por exemplo 'qwen3-coder:480b-cloud'.
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "qwen3:4b")
model = OllamaLLM(model=MODEL_NAME)
chain = prompt | model

# Inicializa agente local de index/search (não crítico — falhará com mensagem)
try:
    agent = LocalAgent()
except Exception as e:
    print(f"Aviso: não foi possível inicializar LocalAgent: {e}")
    agent = None


def buscar_letra_genius(musica, artista=""):
    print(f"Buscando letra para '{musica}' - '{artista}' na Genius...")
    start = time.time()
    try:
        if artista:
            song = genius.search_song(musica, artista)
        else:
            song = genius.search_song(musica)
        if song and song.lyrics:
            tempo = time.time() - start
            print(f"Letra encontrada em {tempo:.2f} segundos." )
            return song.lyrics
        else:
            tempo = time.time() - start
            print(f"Letra não encontrada após {tempo:.2f} segundos.")
    except Exception as e:
        tempo = time.time() - start
        print(f"Falha ao buscar na Genius após {tempo:.2f} segundos: {e}")
    return None


def extrair_artista_musica(entrada):
    entrada = entrada.lower()
    if " de " in entrada:
        musica, artista = entrada.split(" de ", 1)
        return artista.strip(), musica.strip()
    else:
        return "", entrada.strip()


def safe_invoke(payload: dict):
    """Tenta invocar o chain; em caso de falha de conexão ao cliente HTTP
    (por exemplo Ollama não rodando), devolve um fallback amigável com a
    letra (se presente) para que o bot continue funcionando.
    """
    try:
        return chain.invoke(payload)
    except httpx.ConnectError:
        # Falha ao conectar com o server Ollama/local LLM
        reviews = payload.get("reviews") or ""
        question = payload.get("question") or ""
        return f"[FALLBACK] Não foi possível conectar ao modelo local (Ollama).\n\nPergunta: {question}\n\nConteúdo disponível:\n{reviews}"
    except Exception as e:
        msg = str(e)
        # detect common Ollama model-not-found error and give actionable advice
        if "not found" in msg and "model" in msg:
            return (
                f"[ERRO] Modelo não encontrado: {MODEL_NAME}.\n"
                "Verifique os modelos instalados com `ollama list` e, se quiser baixar o modelo, rode:\n"
                f"  ollama pull {MODEL_NAME}\n\n"
                "Ou defina a variável de ambiente OLLAMA_MODEL para um modelo já instalado, por exemplo:\n"
                "  setx OLLAMA_MODEL \"qwen3-coder:480b-cloud\"\n"
                "e reinicie o terminal/sessão antes de rodar novamente."
            )
        return f"[ERRO] Falha ao gerar resposta: {msg}"

MODELO_CURIOSIDADE = "phi3:mini"

template_curiosidade = """
Você é um especialista em música.
Responda em português do Brasil com UMA única curiosidade ou fato interessante sobre a música "{musica}" do artista "{artista}".
Seja direto e breve (máximo 2 frases). Se não souber, apenas diga que não encontrou fatos.

Curiosidade:
"""
prompt_curiosidade = PromptTemplate.from_template(template_curiosidade)

# 3. Crie o novo LLM e o novo Chain
# (Podemos definir um timeout menor aqui, pois a tarefa é rápida)
try:
    llm_curiosidade = OllamaLLM(model=MODELO_CURIOSIDADE, request_timeout=30.0)
    chain_curiosidade = prompt_curiosidade | llm_curiosidade
except Exception as e:
    print(f"AVISO: Não foi possível carregar o modelo de curiosidade ({MODELO_CURIOSIDADE}). {e}")
    chain_curiosidade = None

# 4. Crie uma nova função "safe_invoke" para a curiosidade
def safe_invoke_curiosidade(musica, artista):
    if not chain_curiosidade:
        return "" # Retorna vazio se o modelo não carregou

    try:
        payload = {"musica": musica, "artista": artista}
        resposta = chain_curiosidade.invoke(payload)
        
        # Limpa a resposta para evitar lixo
        resposta = str(resposta).strip()
        if not resposta or "não encontrei" in resposta.lower() or "não sei" in resposta.lower():
            return ""
            
        return f"\n\n💡 **Curiosidade:**\n{resposta}"
        
    except Exception as e:
        print(f"Erro ao gerar curiosidade: {e}")
        return "" # Falha silenciosamente