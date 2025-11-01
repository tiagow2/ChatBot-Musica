import time
import lyricsgenius
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Token Genius
GENIUS_TOKEN = "x5lnU50yJ34O0nmdOD9NszzrxXl8iz-d_9F8yr1JmSJ7z2MaglqCYwh7gztl1_pW"

genius = lyricsgenius.Genius(GENIUS_TOKEN, timeout=30)  # timeout da pra mudar

# Template do bot
template = """
Você é um expert de letras de música, sempre responda em português do Brasil. Você sabe todas as letras de todas as músicas e devolve as letras das músicas com base no título.


Aqui está a letra da música:
{reviews}

Aqui está o título da música para responder:
{question}
"""

prompt = ChatPromptTemplate.from_template(template)
model = OllamaLLM(model="qwen3:4b")
chain = prompt | model

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
            print(f"Letra encontrada em {tempo:.2f} segundos.")
            return song.lyrics
        else:
            tempo = time.time() - start
            print(f"Letra não encontrada após {tempo:.2f} segundos.")
    except Exception as e:
        tempo = time.time() - start
        print(f"Falha ao buscar na Genius após {tempo:.2f} segundos: {e}")
    return None

# Atualizar essa funcao para extrair o artista e a musica com mais sucesso
def extrair_artista_musica(entrada):
    entrada = entrada.lower()
    if " de " in entrada:
        musica, artista = entrada.split(" de ", 1)
        return artista.strip(), musica.strip()
    else:
        # Se não encontrar 'de', assume só música e deixa artista vazio (melhorar essa parte pra deixar com termos de 'por' ou 'feito' etc)
        return "", entrada.strip()

while True:
    print("\n\n-------------------------------")
    texto = input("Digite o nome da música (q para sair): ").strip()
    if texto.lower() == "q":
        break

    artista, musica = extrair_artista_musica(texto)
    print(f"Solicitando: Música='{musica}' | Artista='{artista}'")

    letra = buscar_letra_genius(musica, artista)
    if letra:
        print("Enviando letra ao modelo Ollama...\n")
        result = chain.invoke({"reviews": letra, "question": texto})
        print("\nResposta do bot:\n")
        print(result)
    else:
        print(f"Desculpe, não encontrei a música '{texto}' nem online.")
