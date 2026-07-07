"""
CLI de chat: pergunta -> busca semântica no PDF -> resposta.

Uso:
    python src/chat.py
"""
from search import answer


def main() -> None:
    print("=== Chat com o PDF ===")
    print("Digite sua pergunta (ou 'sair' para encerrar).\n")
    while True:
        try:
            pergunta = input("Faça sua pergunta: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break

        if not pergunta:
            continue
        if pergunta.lower() in {"sair", "exit", "quit"}:
            print("Encerrando.")
            break

        resposta = answer(pergunta)
        print(f"\nPERGUNTA: {pergunta}")
        print(f"RESPOSTA: {resposta}")
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()
