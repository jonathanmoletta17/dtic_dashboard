import os
from fastapi import APIRouter, HTTPException
from collections import Counter

import glpi_client
# Apenas a função de stats por nível é necessária agora
from logic.metrics_logic import generate_level_stats
from schemas import GeneralStats, LevelStats

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
async def get_level_stats_endpoint():
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
        level_data = generate_level_stats(api_url=API_URL, session_headers=headers)
        return level_data
    except Exception as e:
        print(f"❌ Erro no endpoint /status-niveis: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao buscar estatísticas por nível: {e}")


@router.get(
    "/metrics-gerais",
    response_model=GeneralStats,
    summary="Obtém estatísticas gerais de tickets",
)
async def get_general_stats_endpoint():
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
        # 1. Busca os dados detalhados por nível
        level_data = generate_level_stats(api_url=API_URL, session_headers=headers)

        # 2. Calcula os totais gerais somando os valores de cada nível
        total_stats = Counter()
        for level_name, level_data_dict in level_data.items():
            # level_data_dict é um dicionário com as contagens por status
            for status_name, count in level_data_dict.items():
                if status_name != 'total':  # Ignora o campo 'total' para evitar duplicação
                    total_stats[status_name] += count

        # 3. Formata para o schema de resposta esperado
        general_stats = {
            "novos": total_stats.get('novos', 0),
            "em_progresso": total_stats.get('em_progresso', 0),
            "pendentes": total_stats.get('pendentes', 0),
            "resolvidos": total_stats.get('resolvidos', 0),
        }
        return general_stats

    except Exception as e:
        print(f"❌ Erro no endpoint /metrics-gerais: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao buscar métricas gerais: {e}")
