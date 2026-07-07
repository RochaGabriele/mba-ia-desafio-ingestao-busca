-- Habilita a extensão pgVector no banco (executado no 1º start do container).
-- O langchain_postgres também tenta criar a extensão, mas garantimos aqui.
CREATE EXTENSION IF NOT EXISTS vector;
