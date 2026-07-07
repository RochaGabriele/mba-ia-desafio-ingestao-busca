"""
Ingestão do PDF para o banco vetorial (PostgreSQL + pgVector).

Fluxo:
  1. Carrega o PDF (PyPDFLoader)
  2. Divide em chunks de 1000 caracteres com overlap de 150
  3. Gera embeddings (Google embedding-001)
  4. Salva os vetores no PGVector

Uso:
    python src/ingest.py
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH", "document.pdf")
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION = os.getenv("PGVECTOR_COLLECTION", "pdf_documents")
EMBEDDING_MODEL = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001")


def main() -> None:
    if not DATABASE_URL:
        raise SystemExit("DATABASE_URL não definido. Copie .env.example para .env e preencha.")
    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit("GOOGLE_API_KEY não definido no .env.")

    pdf = Path(PDF_PATH)
    if not pdf.exists():
        raise SystemExit(f"PDF não encontrado: {pdf.resolve()}")

    print(f"Lendo PDF: {pdf}")
    docs = PyPDFLoader(str(pdf)).load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(docs)
    print(f"{len(chunks)} chunks gerados (1000 chars / overlap 150).")

    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    store = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION,
        connection=DATABASE_URL,
        use_jsonb=True,
        pre_delete_collection=True,  # recarrega do zero a cada ingestão
    )

    ids = [f"chunk-{i}" for i in range(len(chunks))]
    store.add_documents(chunks, ids=ids)
    print(f"Ingestão concluída: {len(chunks)} vetores na coleção '{COLLECTION}'.")


if __name__ == "__main__":
    main()
