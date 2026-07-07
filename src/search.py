"""
Busca semântica + montagem do prompt + chamada da LLM.

Passos ao receber uma pergunta:
  1. Vetoriza a pergunta e busca os 10 resultados mais relevantes (k=10).
  2. Concatena o conteúdo dos resultados como CONTEXTO.
  3. Monta o prompt e chama a LLM (Gemini).
  4. Retorna a resposta.

Expõe `answer(question)`, usada pelo chat.py.
"""
import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION = os.getenv("PGVECTOR_COLLECTION", "pdf_documents")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001")
LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL", "gemini-2.5-flash-lite")

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
""".strip()

_store = None
_llm = None


def get_store() -> PGVector:
    """Conexão com o PGVector (criada uma vez e reutilizada)."""
    global _store
    if _store is None:
        if not DATABASE_URL:
            raise SystemExit("DATABASE_URL não definido. Copie .env.example para .env e preencha.")
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        _store = PGVector(
            embeddings=embeddings,
            collection_name=COLLECTION,
            connection=DATABASE_URL,
            use_jsonb=True,
        )
    return _store


def get_llm() -> ChatGoogleGenerativeAI:
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0)
    return _llm


def answer(question: str) -> str:
    """Recebe a pergunta e devolve a resposta baseada apenas no PDF."""
    results = get_store().similarity_search_with_score(question, k=10)
    contexto = "\n\n".join(doc.page_content for doc, _score in results)

    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=question)
    resposta = get_llm().invoke(prompt)
    return resposta.content.strip()


if __name__ == "__main__":
    import sys

    pergunta = " ".join(sys.argv[1:]) or "Qual o faturamento da Empresa SuperTechIABrazil?"
    print(answer(pergunta))
