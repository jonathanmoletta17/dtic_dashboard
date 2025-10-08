import logging
import os
from typing import List

from fastapi import APIRouter, HTTPException, Query

import backend.glpi_client as glpi_client
from backend.logic.errors import GLPIAuthError, GLPINetworkError, GLPISearchError
from backend.logic.ranking_logic import generate_technician_ranking
from backend.schemas import TechnicianRankingItem
from backend.utils.cache import cache
from backend.utils.logging_setup import format_range

# Cria um novo roteador com um prefixo para todas as suas rotas
router = APIRouter(
    prefix="/api/v1",
    tags=["Ranking"],  # Agrupa endpoints na documentação da API
)

logger = logging.getLogger(__name__)

RANKING_LIMIT = 20   # quantidade máxima de itens retornados pelo endpoint
CACHE_TTL_SEC = int(os.getenv("CACHE_TTL_SEC", "300"))


@router.get(
    "/ranking-tecnicos",
    response_model=List[TechnicianRankingItem],
    summary="Gera o ranking de técnicos",
    description="Retorna uma lista ordenada de técnicos pelo número de tickets atribuídos."
)
async def get_ranking_tecnicos_endpoint(
    inicio: str | None = Query(default=None, description="Data inicial no formato YYYY-MM-DD"),
    fim: str | None = Query(default=None, description="Data final no formato YYYY-MM-DD"),
):
    """
    Endpoint para obter o ranking de técnicos.
    Este endpoint lida com a autenticação e chama a lógica de negócio para gerar os dados.
    """
    # Chave de cache inclui endpoint, intervalo e limite
    key = (
        f"ranking-tecnicos|inicio={inicio or ''}|fim={fim or ''}|limit={RANKING_LIMIT}"
    )
    cached = cache.get(key)
    if cached is not None:
        logger.info(
            "cache_hit=true endpoint=/ranking-tecnicos itemtype=Ticket range=%s key=%s limit=%s",
            format_range(inicio, fim),
            key,
            RANKING_LIMIT,
        )
        return cached
    logger.info(
        "cache_hit=false endpoint=/ranking-tecnicos itemtype=Ticket range=%s key=%s limit=%s",
        format_range(inicio, fim),
        key,
        RANKING_LIMIT,
    )
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
        ranking_data = generate_technician_ranking(
            api_url=API_URL,
            session_headers=headers,
            inicio=inicio,
            fim=fim,
        )

        # Retorna Top N e grava em cache (TTL curto)
        top_data = ranking_data[:RANKING_LIMIT]
        cache.set(key, top_data, ttl=CACHE_TTL_SEC)
        logger.info(
            "cache_set endpoint=/ranking-tecnicos itemtype=Ticket range=%s key=%s limit=%s ttl=%s",
            format_range(inicio, fim),
            key,
            RANKING_LIMIT,
            CACHE_TTL_SEC,
        )
        return top_data
    except GLPIAuthError as e:
        status = e.status_code or 401
        logger.warning("endpoint=/ranking-tecnicos itemtype=Ticket error=GLPIAuthError glpi_status=%s", status)
        raise HTTPException(status_code=status, detail="Falha de autenticação com GLPI.")
    except GLPINetworkError as e:
        status = 504 if e.timeout else 502
        net_status = "timeout" if e.timeout else "network"
        logger.error("endpoint=/ranking-tecnicos itemtype=Ticket error=GLPINetworkError glpi_status=%s", net_status)
        raise HTTPException(status_code=status, detail="Falha de comunicação com serviço GLPI.")
    except GLPISearchError as e:
        status = e.status_code or 502
        logger.error("endpoint=/ranking-tecnicos itemtype=Ticket error=GLPISearchError glpi_status=%s", status)
        raise HTTPException(status_code=status, detail="Erro ao consultar dados do GLPI.")
