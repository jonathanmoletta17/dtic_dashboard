import logging
import os

from fastapi import APIRouter, HTTPException, Query

import backend.glpi_client as glpi_client
from backend.logic.errors import GLPIAuthError, GLPINetworkError, GLPISearchError
from backend.logic.glpi_constants import STATUS

# Apenas a função de stats por nível é necessária agora
from backend.logic.metrics_logic import generate_general_stats, generate_level_stats
from backend.schemas import GeneralStats, LevelStats
from backend.utils.cache import cache
from backend.utils.logging_setup import format_range

# Cria um novo roteador com um prefixo e tags para a documentação
router = APIRouter(
    prefix="/api/v1",
    tags=["Statistics"],
)

logger = logging.getLogger(__name__)

# TTL explícito para set de cache
CACHE_TTL_SEC = int(os.getenv("CACHE_TTL_SEC", "300"))

@router.get(
    "/status-niveis",
    response_model=LevelStats,
    summary="Obtém contagem de tickets por nível de atendimento",
)
async def get_level_stats_endpoint(
    inicio: str | None = Query(default=None, description="Data inicial no formato YYYY-MM-DD"),
    fim: str | None = Query(default=None, description="Data final no formato YYYY-MM-DD"),
):
    """
    Endpoint para obter uma contagem de tickets para cada nível de suporte (N1, N2, N3, N4).
    """
    # Definir chave de cache ANTES de qualquer uso
    key = f"status-niveis|inicio={inicio or ''}|fim={fim or ''}"
    cached = cache.get(key)
    if cached is not None:
        logger.info(
            "cache_hit=true endpoint=/status-niveis itemtype=Ticket range=%s key=%s",
            format_range(inicio, fim),
            key,
        )
        return cached
    logger.info(
        "cache_hit=false endpoint=/status-niveis itemtype=Ticket range=%s key=%s",
        format_range(inicio, fim),
        key,
    )

    API_URL = os.getenv("API_URL")
    APP_TOKEN = os.getenv("APP_TOKEN")
    USER_TOKEN = os.getenv("USER_TOKEN")

    if not all([API_URL, APP_TOKEN, USER_TOKEN]):
        raise HTTPException(status_code=500, detail="Variáveis de ambiente da API não configuradas.")

    try:
        headers = glpi_client.authenticate(API_URL, APP_TOKEN, USER_TOKEN)
        level_data = generate_level_stats(
            api_url=API_URL,
            session_headers=headers,
            inicio=inicio,
            fim=fim,
        )
        cache.set(key, level_data, ttl=CACHE_TTL_SEC)
        logger.info(
            "cache_set endpoint=/status-niveis itemtype=Ticket range=%s key=%s ttl=%s",
            format_range(inicio, fim),
            key,
            CACHE_TTL_SEC,
        )
        return level_data
    except GLPIAuthError as e:
        status = e.status_code or 401
        logger.warning("endpoint=/status-niveis itemtype=Ticket error=GLPIAuthError glpi_status=%s", status)
        raise HTTPException(status_code=status, detail="Falha de autenticação com GLPI.")
    except GLPINetworkError as e:
        status = 504 if e.timeout else 502
        net_status = "timeout" if e.timeout else "network"
        logger.error("endpoint=/status-niveis itemtype=Ticket error=GLPINetworkError glpi_status=%s", net_status)
        raise HTTPException(status_code=status, detail="Falha de comunicação com serviço GLPI.")
    except GLPISearchError as e:
        status = e.status_code or 502
        logger.error("endpoint=/status-niveis itemtype=Ticket error=GLPISearchError glpi_status=%s", status)
        raise HTTPException(status_code=status, detail="Erro ao consultar dados do GLPI.")


@router.get(
    "/metrics-gerais",
    response_model=GeneralStats,
    summary="Obtém estatísticas gerais de tickets",
)
async def get_general_stats_endpoint(
    inicio: str | None = Query(default=None, description="Data inicial no formato YYYY-MM-DD"),
    fim: str | None = Query(default=None, description="Data final no formato YYYY-MM-DD"),
):
    """
    Endpoint para obter uma contagem geral de tickets por status.
    Os dados são derivados a partir dos dados detalhados por nível para garantir consistência.
    """
    # Definir chave de cache ANTES de qualquer uso
    # Construir parte de status com base nos valores do dicionário STATUS em ordem conhecida
    status_part = ",".join(
        [
            str(STATUS["NEW"]),
            str(STATUS["ASSIGNED"]),
            str(STATUS["PLANNED"]),
            str(STATUS["IN_PROGRESS"]),
            str(STATUS["SOLVED"]),
            str(STATUS["CLOSED"]),
        ]
    )
    key = f"metrics-gerais|inicio={inicio or ''}|fim={fim or ''}|status={status_part}"
    cached = cache.get(key)
    if cached is not None:
        logger.info(
            "cache_hit=true endpoint=/metrics-gerais itemtype=Ticket range=%s status_set=%s key=%s",
            format_range(inicio, fim),
            status_part,
            key,
        )
        return cached
    logger.info(
        "cache_hit=false endpoint=/metrics-gerais itemtype=Ticket range=%s status_set=%s key=%s",
        format_range(inicio, fim),
        status_part,
        key,
    )

    API_URL = os.getenv("API_URL")
    APP_TOKEN = os.getenv("APP_TOKEN")
    USER_TOKEN = os.getenv("USER_TOKEN")

    if not all([API_URL, APP_TOKEN, USER_TOKEN]):
        raise HTTPException(status_code=500, detail="Variáveis de ambiente da API não configuradas.")

    try:
        headers = glpi_client.authenticate(API_URL, APP_TOKEN, USER_TOKEN)
        # Contagem direta no GLPI por Status (FIELD_STATUS), com filtro opcional por intervalo de datas
        general_stats = generate_general_stats(
            api_url=API_URL,
            session_headers=headers,
            inicio=inicio,
            fim=fim,
        )
        cache.set(key, general_stats, ttl=CACHE_TTL_SEC)
        logger.info(
            "cache_set endpoint=/metrics-gerais itemtype=Ticket range=%s status_set=%s key=%s ttl=%s",
            format_range(inicio, fim),
            status_part,
            key,
            CACHE_TTL_SEC,
        )
        return general_stats

    except GLPIAuthError as e:
        status = e.status_code or 401
        logger.warning("endpoint=/metrics-gerais itemtype=Ticket error=GLPIAuthError glpi_status=%s", status)
        raise HTTPException(status_code=status, detail="Falha de autenticação com GLPI.")
    except GLPINetworkError as e:
        status = 504 if e.timeout else 502
        net_status = "timeout" if e.timeout else "network"
        logger.error("endpoint=/metrics-gerais itemtype=Ticket error=GLPINetworkError glpi_status=%s", net_status)
        raise HTTPException(status_code=status, detail="Falha de comunicação com serviço GLPI.")
    except GLPISearchError as e:
        status = e.status_code or 502
        logger.error("endpoint=/metrics-gerais itemtype=Ticket error=GLPISearchError glpi_status=%s", status)
        raise HTTPException(status_code=status, detail="Erro ao consultar dados do GLPI.")
