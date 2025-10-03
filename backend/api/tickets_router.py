import os
from typing import List
from fastapi import APIRouter, HTTPException

import backend.glpi_client as glpi_client
from backend.logic.tickets_logic import get_new_tickets
from backend.schemas import NewTicketItem

# Cria um novo roteador
router = APIRouter(
    prefix="/api/v1",
    tags=["Tickets"],
)


@router.get(
    "/tickets-novos",
    response_model=List[NewTicketItem],
    summary="Lista os 10 tickets mais recentes com status 'Novo'",
)
async def get_new_tickets_endpoint():
    """
    Endpoint para obter uma lista dos 10 tickets mais recentes com status 'Novo'.
    """
    API_URL = os.getenv("API_URL")
    APP_TOKEN = os.getenv("APP_TOKEN")
    USER_TOKEN = os.getenv("USER_TOKEN")

    if not all([API_URL, APP_TOKEN, USER_TOKEN]):
        raise HTTPException(status_code=500, detail="Variáveis de ambiente da API não configuradas.")

    try:
        headers = glpi_client.authenticate(API_URL, APP_TOKEN, USER_TOKEN)
        tickets_data = get_new_tickets(api_url=API_URL, session_headers=headers)
        return tickets_data
    except Exception as e:
        print(f"❌ Erro no endpoint /tickets-novos: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao buscar tickets novos: {e}")
