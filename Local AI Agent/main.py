import pandas as pd
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

# Ler o CSV com as músicas e letras
df = pd.read_csv("letras_de_musicas.csv")

# Inicializa o modelo Ollama
model = OllamaLLM(model="qwen3:4b")

# Template com placeholders para a letra e título da música
template = """
Você é um expert de letras de música, você sabe todas as letras de todas as músicas e devolve as letras das músicas com base no título.

Aqui está a letra da música:
{reviews}

Aqui está o título da música para responder:
{question}
"""

# Cria o prompt template com from_template
prompt = ChatPromptTemplate.from_template(template)

# Cria a chain combinando prompt e modelo
chain = prompt | model

while True:
    print("\n\n-------------------------------")
    musica = input("Digite o nome da música (q para sair): ")
    print("\n")
    if musica.lower() == "q":
        break

    # Buscar letra da música no CSV (case insensitive)
    row = df[df['musica'].str.lower() == musica.lower()]
    if row.empty:
        print(f"Desculpe, não encontrei a música '{musica}'.")
        continue

    letra = row.iloc[0]['letra']

    # Executa a chain passando a letra e o nome da música
    result = chain.invoke({"reviews": letra, "question": musica})

    print("\nResposta do bot:\n")
    print(result)
