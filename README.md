# Ingestão e Busca Semântica com LangChain e Postgres (pgVector)

Software que faz **ingestão de um PDF** em um banco **PostgreSQL + pgVector** e permite **perguntas via CLI**, respondendo **apenas com base no conteúdo do PDF**.

Provedor de IA: **Google Gemini** (embeddings `models/gemini-embedding-001` + LLM `gemini-2.5-flash-lite`).

```
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.

PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

## Estrutura

```
├── docker-compose.yml     # Postgres + pgVector
├── init.sql               # habilita a extensão vector
├── requirements.txt       # dependências
├── .env.example           # template de variáveis de ambiente
├── src/
│   ├── ingest.py          # ingestão do PDF
│   ├── search.py          # busca semântica + prompt + LLM
│   └── chat.py            # CLI de interação
├── document.pdf           # PDF para ingestão
└── README.md
```

## Pré-requisitos

- **Python 3.10+**
- **Docker Desktop** (para subir o Postgres+pgVector)
- **Chave de API do Google Gemini** — crie em https://aistudio.google.com/app/apikey

## Passo a passo

### 1. Ambiente virtual e dependências

```powershell
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate       # Linux/macOS
pip install -r requirements.txt
```

### 2. Variáveis de ambiente

Copie o template e preencha sua chave do Google:

```powershell
Copy-Item .env.example .env      # Windows
# cp .env.example .env           # Linux/macOS
```

Edite o `.env` e defina `GOOGLE_API_KEY`.

### 3. Subir o banco de dados

```bash
docker compose up -d
```

### 4. Ingerir o PDF

Coloque o arquivo a ser lido como `document.pdf` na raiz (ou ajuste `PDF_PATH` no `.env`) e rode:

```bash
python src/ingest.py
```

### 5. Rodar o chat

```bash
python src/chat.py
```

Digite perguntas no terminal. Use `sair` para encerrar.

## Como funciona

- **Ingestão** (`ingest.py`): `PyPDFLoader` lê o PDF → `RecursiveCharacterTextSplitter` divide em chunks de **1000** caracteres com **overlap 150** → cada chunk vira embedding (`gemini-embedding-001`) → vetores salvos no `PGVector`.
- **Busca** (`search.py`): a pergunta é vetorizada → `similarity_search_with_score(query, k=10)` traz os 10 chunks mais relevantes → são concatenados no `CONTEXTO` do prompt → a LLM responde **estritamente** com base nesse contexto.
- **CLI** (`chat.py`): loop de perguntas e respostas no terminal.

## Observações

- O `.env` **não** deve ser commitado (já está no `.gitignore`).
- Se `gemini-2.5-flash-lite` ficar indisponível, troque `GOOGLE_LLM_MODEL` no `.env` por outro modelo Gemini (ex.: `gemini-2.0-flash`). Limites do free tier mudam com frequência — consulte a documentação oficial do Google.
