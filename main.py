"""
Ponto de entrada raiz que delega para o módulo app.main.
Compatível com a estrutura de backend de agent-chat-sse-fastapi-01.
"""

from app.main import main, app

if __name__ == "__main__":
    main()
