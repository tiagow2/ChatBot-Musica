from ai_core import buscar_letra_genius, extrair_artista_musica, chain, agent, safe_invoke
from mcp_client import is_alive, add_doc as mcp_add, search as mcp_search
import requests
import time


def run_cli():
    while True:
        print("\n\n-------------------------------")
        texto = input("Digite o nome da música (q para sair): ").strip()
        if texto.lower() == "q":
            break
        artista, musica = extrair_artista_musica(texto)
        print(f"Solicitando: Música='{musica}' | Artista='{artista}'")
        letra = buscar_letra_genius(musica, artista)
        if letra:
            # tenta indexar no MCP HTTP (central). Se não, usa LocalAgent como fallback.
            doc_id = f"{artista or 'unknown'}-{musica}".strip().lower()
            posted = False
            try:
                # checa disponibilidade do MCP no início desta iteração
                mcp_available = is_alive()
            except Exception:
                mcp_available = False

            if mcp_available:
                try:
                    posted = mcp_add(doc_id, letra, {"music": musica, "artist": artista})
                    if posted:
                        print("Documento salvo no MCP server (mcp.sqlite).")
                except Exception:
                    posted = False

            if not posted:
                # indexa a letra no agente local para buscas futuras
                if agent:
                    try:
                        agent.add_document(doc_id, letra, {"music": musica, "artist": artista})
                        print("Documento salvo no LocalAgent (metadata.db).")
                    except Exception as e:
                        print(f"Falha ao indexar documento no agente local: {e}")

            # busca documentos similares à pergunta para enriquecer o prompt
            reviews_text = letra
            try:
                # preferir MCP se disponível (usando a mesma checagem rápida)
                if 'mcp_available' not in locals():
                    try:
                        mcp_available = is_alive()
                    except Exception:
                        mcp_available = False

                if mcp_available:
                    similares = mcp_search(texto, k=2)
                    if similares:
                        combined = [s.get("text", "") for s in similares]
                        reviews_text = "\n\n--- Similar ---\n\n".join(["\n\n".join(combined), letra])
                else:
                    if agent:
                        similares = agent.search(texto, k=2)
                        if similares:
                            combined = [s.get("text", "") for s in similares]
                            reviews_text = "\n\n--- Similar ---\n\n".join(["\n\n".join(combined), letra])
            except Exception as e:
                print(f"Falha na busca por similares: {e}")

            print("Enviando letra ao modelo Ollama (ou fallback) ...\n")
            result = safe_invoke({"reviews": reviews_text, "question": texto})
            print("\nResposta do bot:\n")
            print(result)
        else:
            print(f"Desculpe, não encontrei a música '{texto}' nem online.")


if __name__ == "__main__":
    try:
        run_cli()
    finally:
        if agent:
            try:
                agent.close()
            except Exception:
                pass
