import os
from typing import List
import time
from fastapi import APIRouter, HTTPException
from fastapi import Query

import backend.glpi_client as glpi_client
from backend.logic.ranking_logic import generate_technician_ranking
from backend.schemas import TechnicianRankingItem

# Cria um novo roteador com um prefixo para todas as suas rotas
router = APIRouter(
    prefix="/api/v1",
    tags=["Ranking"],  # Agrupa endpoints na documentação da API
)

# Cache simples em memória para o ranking (TTL curto)
_CACHE_DATA: List[TechnicianRankingItem] = []
_CACHE_TS: float = 0.0
CACHE_TTL_SEC = 600  # atualiza a cada 10 minutos para reduzir recomputações
RANKING_LIMIT = 20   # quantidade máxima de itens retornados pelo endpoint


@router.get(
    "/ranking-tecnicos",
    response_model=List[TechnicianRankingItem],
    summary="Gera o ranking de técnicos",
    description="Retorna uma lista ordenada de técnicos pelo número de tickets atribuídos."
)
async def get_ranking_tecnicos_endpoint():
    """
    Endpoint para obter o ranking de técnicos.
    Este endpoint lida com a autenticação e chama a lógica de negócio para gerar os dados.
    """
    # Retorna do cache se ainda válido
    global _CACHE_DATA, _CACHE_TS
    now = time.time()
    if _CACHE_DATA and (now - _CACHE_TS) < CACHE_TTL_SEC:
        return _CACHE_DATA
    # As variáveis são lidas de dentro da função para garantir que o .env já foi carregado
    API_URL = os.getenv("API_URL")
    APP_TOKEN = os.getenv("APP_TOKEN")
    USER_TOKEN = os.getenv("USER_TOKEN")

    if not all([API_URL, APP_TOKEN, USER_TOKEN]):
        raise HTTPException(
            status_code=500,
            detail="As variáveis de ambiente da API do GLPI não foram configuradas corretamente."
        )

    try:
        # Autenticação é feita aqui, na camada da API
        headers = glpi_client.authenticate(API_URL, APP_TOKEN, USER_TOKEN)

        # Chama a lógica de negócio, injetando as dependências
        ranking_data = generate_technician_ranking(api_url=API_URL, session_headers=headers)

        # Retorna e atualiza cache (Top N)
        _CACHE_DATA = ranking_data[:RANKING_LIMIT]
        _CACHE_TS = time.time()
        return _CACHE_DATA

    except Exception as e:
        # Log do erro no servidor para depuração
        print(f"❌ Erro no endpoint /ranking-tecnicos: {e}")
        # Retorna uma resposta de erro genérica para o cliente
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro interno ao gerar o ranking: {e}",
        ) from e
