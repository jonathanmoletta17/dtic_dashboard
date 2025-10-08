"""
Backend FastAPI: Ponto de entrada principal da aplicação.
Este arquivo inicializa a aplicação FastAPI e inclui os roteadores modulares.
"""
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Constrói o caminho absoluto para o arquivo .env dentro da pasta 'backend'
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# Carrega as variáveis de ambiente do caminho especificado
load_dotenv(dotenv_path=dotenv_path)

# Configuração central de logging
from backend.utils.logging_setup import configure_logging

configure_logging()

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

"""Montagem de estáticos do frontend em /dashboard.
Usamos StaticFiles com html=True para que quaisquer rotas desconhecidas
retornem index.html sem interceptar assets (JS/CSS) corretamente.
"""
FRONTEND_BUILD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend_build")
if os.path.isdir(FRONTEND_BUILD_DIR):
    # Monta o frontend sob /dashboard, garantindo que assets em /dashboard/assets
    # sejam servidos corretamente e que rotas SPA como /dashboard/dtic façam fallback
    # para index.html via html=True
    app.mount("/dashboard", StaticFiles(directory=FRONTEND_BUILD_DIR, html=True), name="dashboard")

    # Fallback explícito para a rota canônica do app DTIC sem barra final,
    # evitando 404 em /dashboard/dtic (o StaticFiles retorna index.html quando há barra).
    INDEX_HTML = os.path.join(FRONTEND_BUILD_DIR, "index.html")

    @app.get("/dashboard/dtic")
    def serve_dtic_index():
        return FileResponse(INDEX_HTML)

    @app.get("/dashboard/dtic/")
    def serve_dtic_index_slash():
        return FileResponse(INDEX_HTML)

# O bloco a seguir permite a execução direta para depuração
if __name__ == "__main__":
    import uvicorn
    logging.getLogger(__name__).info(
        "endpoint=/ __main__=true msg=Starting Uvicorn dev server host=0.0.0.0 port=8000"
    )
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)