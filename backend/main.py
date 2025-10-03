"""
Backend FastAPI: Ponto de entrada principal da aplicação.
Este arquivo inicializa a aplicação FastAPI e inclui os roteadores modulares.
"""
import os
from fastapi import FastAPI
from dotenv import load_dotenv

# Constrói o caminho absoluto para o arquivo .env dentro da pasta 'backend'
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# Carrega as variáveis de ambiente do caminho especificado
load_dotenv(dotenv_path=dotenv_path)

# Os roteadores são importados DEPOIS que as variáveis de ambiente foram carregadas
from backend.api import ranking_router, stats_router, tickets_router

# Cria a instância principal da aplicação FastAPI
app = FastAPI(
    title="GLPI Dashboard API",
    description="API para fornecer dados de tickets do GLPI para o dashboard.",
    version="3.1.0" # Bump de versão para refletir a correção final
)

# Adiciona um endpoint raiz para verificação de status
@app.get("/")
def read_root():
    """Endpoint raiz para verificar se a API está funcionando."""
    return {"message": "GLPI Dashboard API", "version": app.version}

# Inclui os roteadores modulares na aplicação principal
app.include_router(ranking_router.router)
app.include_router(stats_router.router)
app.include_router(tickets_router.router)

# O bloco a seguir permite a execução direta para depuração
if __name__ == "__main__":
    import uvicorn
    print("Iniciando servidor Uvicorn para desenvolvimento em http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)