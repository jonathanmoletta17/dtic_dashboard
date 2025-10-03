import os
from fastapi import APIRouter, HTTPException, Query
from collections import Counter

import backend.glpi_client as glpi_client
# Apenas a função de stats por nível é necessária agora
from backend.logic.metrics_logic import generate_level_stats, generate_general_stats
from backend.schemas import GeneralStats, LevelStats

# Cria um novo roteador com um prefixo e tags para a documentação
router = APIRouter(
    prefix="/api/v1",
    tags=["Statistics"],
)

@router.get(
    "/status-niveis",
    response_model=LevelStats,
    summary="Obtém contagem de tickets por nível de atendimento",
)
async def get_level_stats_endpoint(
    inicio: str | None = Query(default=None, description="Data inicial no formato YYYY-MM-DD"),
    fim: str | None = Query(default=None, description="Data final no formato YYYY-MM-DD"),
    campo_data: int | None = Query(default=15, description="Campo de data (15=criação, 19=modificação)"),
):
    """
    Endpoint para obter uma contagem de tickets para cada nível de suporte (N1, N2, N3, N4).
    """
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
            campo_data=campo_data or 15,
        )
        return level_data
    except Exception as e:
        print(f"❌ Erro no endpoint /status-niveis: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao buscar estatísticas por nível: {e}")


@router.get(
    "/metrics-gerais",
    response_model=GeneralStats,
    summary="Obtém estatísticas gerais de tickets",
)
async def get_general_stats_endpoint(
    inicio: str | None = Query(default=None, description="Data inicial no formato YYYY-MM-DD"),
    fim: str | None = Query(default=None, description="Data final no formato YYYY-MM-DD"),
    campo_data: int | None = Query(default=15, description="Campo de data (15=criação, 19=modificação)"),
):
    """
    Endpoint para obter uma contagem geral de tickets por status.
    Os dados são derivados a partir dos dados detalhados por nível para garantir consistência.
    """
    API_URL = os.getenv("API_URL")
    APP_TOKEN = os.getenv("APP_TOKEN")
    USER_TOKEN = os.getenv("USER_TOKEN")

    if not all([API_URL, APP_TOKEN, USER_TOKEN]):
        raise HTTPException(status_code=500, detail="Variáveis de ambiente da API não configuradas.")

    try:
        headers = glpi_client.authenticate(API_URL, APP_TOKEN, USER_TOKEN)
        # Contagem direta no GLPI por Status (campo 12), com filtro opcional por intervalo de datas
        general_stats = generate_general_stats(
            api_url=API_URL,
            session_headers=headers,
            inicio=inicio,
            fim=fim,
            campo_data=campo_data or 15,
        )
        return general_stats

    except Exception as e:
        print(f"❌ Erro no endpoint /metrics-gerais: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao buscar métricas gerais: {e}")
