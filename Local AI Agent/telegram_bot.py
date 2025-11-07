"""Bot Telegram simples integrado ao chain do `ai_core`.

Funcionalidades:
 - Texto: responde usando o chain (chain.invoke)
 - Áudio (mensagem de voz): baixa o ficheiro, salva temporariamente, transcreve com Whisper e responde

Requisitos:
 - TELEGRAM_TOKEN no ambiente ou alterar abaixo
 - pip install pyTelegramBotAPI openai-whisper
 - ffmpeg disponível no PATH para que Whisper funcione
"""

import os
import tempfile
import telebot
from ai_core import chain
from mcp_client import is_alive as mcp_is_alive, add_doc as mcp_add
import time

try:
    import whisper
except Exception:
    whisper = None

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", None)
if not TELEGRAM_TOKEN:
    raise RuntimeError("Defina a variável de ambiente TELEGRAM_TOKEN com o token do seu bot")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# checa disponibilidade do MCP uma vez ao iniciar o bot (será rechecado antes de postar)
try:
    MCP_AVAILABLE_AT_START = mcp_is_alive()
    if MCP_AVAILABLE_AT_START:
        print("MCP server detectado: usando MCP para persistência de transcrições.")
    else:
        print("MCP server não detectado: o bot usará fallback local quando aplicável.")
except Exception:
    MCP_AVAILABLE_AT_START = False


@bot.message_handler(func=lambda message: True)
def reply_hi(message):
    try:
        from ai_core import buscar_letra_genius, extrair_artista_musica
        
        q = message.text or ""
        artista, musica = extrair_artista_musica(q)
        
        letra = buscar_letra_genius(musica, artista)
        
        if not letra:
            bot.reply_to(message, f"Desculpe, não encontrei a letra de '{q}'. Tente outro formato, como: 'Bohemian Rhapsody de Queen'")
            return
        
        if len(letra) > 4000:
            letra = letra[:4000] + "\n\n... (letra truncada - muito longa para o Telegram)"
        
        bot.reply_to(message, f"🎵 {musica.title()} - {artista.title() if artista else 'Artista desconhecido'}\n\n{letra}")
    
    except Exception as e:
        bot.reply_to(message, f"Erro ao gerar resposta: {e}")


@bot.message_handler(content_types=["voice"])
def transcribe_voice_message(message):
    try:
        from ai_core import buscar_letra_genius, extrair_artista_musica, safe_invoke
        
        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        file_bytes = bot.download_file(file_path)

        # salva o arquivo temporariamente
        suffix = os.path.splitext(file_path)[1] or ".ogg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(file_bytes)
            tmp_path = f.name

        text = whisper_transcribe(tmp_path)
        # remove o arquivo temporário
        try:
            os.remove(tmp_path)
        except Exception:
            pass

        # postar no MCP se disponível
        doc_id = f"telegram-voice-{message.message_id}"
        try:
                # re-checar disponibilidade rapidamente antes de postar
                try:
                    if mcp_is_alive():
                        ok = mcp_add(doc_id, text, {"source": "telegram_voice", "user": message.from_user.id})
                        if ok:
                            print("Transcrição salva no MCP server.")
                    else:
                        print("MCP não disponível no momento; pulando persistência remota.")
                except Exception:
                    print("Falha ao tentar salvar transcrição no MCP; pulando persistência remota.")
        except Exception:
            pass

        # busca a letra
        artista, musica = extrair_artista_musica(text)
        letra = buscar_letra_genius(musica, artista)
        
        if not letra:
            bot.reply_to(message, f"Transcrição: '{text}'\n\nNão encontrei a letra. Tente reformular.")
            return
        
        resp = safe_invoke({"question": text, "reviews": letra})
        bot.reply_to(message, str(resp))
    except Exception as e:
        bot.reply_to(message, f"Erro no processamento do áudio: {e}")


def whisper_transcribe(filepath: str, model_name: str = "tiny") -> str:
    """Transcreve um arquivo de áudio utilizando Whisper.

    Observação: Whisper (openai-whisper) requer ffmpeg instalado no sistema.
    """
    if whisper is None:
        raise RuntimeError("whisper não está instalado. Instale com: pip install openai-whisper")

    model = whisper.load_model(model_name)
    result = model.transcribe(filepath)
    return result.get("text", "")


if __name__ == "__main__":
    print("Iniciando Telegram bot...")
    bot.polling()
