import os
from typing import List
from fastapi import APIRouter, HTTPException

import glpi_client
from logic.ranking_logic import generate_technician_ranking
from schemas import TechnicianRankingItem

# Cria um novo roteador com um prefixo para todas as suas rotas
router = APIRouter(
    prefix="/api/v1",
    tags=["Ranking"],  # Agrupa endpoints na documentação da API
)


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
        
        # Retorna o top 10 para manter compatibilidade com o frontend
        return ranking_data[:10]
        
    except Exception as e:
        # Log do erro no servidor para depuração
        print(f"❌ Erro no endpoint /ranking-tecnicos: {e}")
        # Retorna uma resposta de erro genérica para o cliente
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno ao gerar o ranking: {e}")
