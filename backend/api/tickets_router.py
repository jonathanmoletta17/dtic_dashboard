import logging
import os
from typing import List

from fastapi import APIRouter, HTTPException

import backend.glpi_client as glpi_client
from backend.logic.errors import GLPIAuthError, GLPINetworkError, GLPISearchError
from backend.logic.tickets_logic import get_new_tickets
from backend.schemas import NewTicketItem

# Cria um novo roteador
router = APIRouter(
    prefix="/api/v1",
    tags=["Tickets"],
)

logger = logging.getLogger(__name__)


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
        logger.info("endpoint=/tickets-novos itemtype=Ticket count=%s", len(tickets_data))
        return tickets_data
    except GLPIAuthError as e:
        status = e.status_code or 401
        logger.warning("endpoint=/tickets-novos itemtype=Ticket error=GLPIAuthError glpi_status=%s", status)
        raise HTTPException(status_code=status, detail="Falha de autenticação com GLPI.")
    except GLPINetworkError as e:
        status = 504 if e.timeout else 502
        net_status = "timeout" if e.timeout else "network"
        logger.error("endpoint=/tickets-novos itemtype=Ticket error=GLPINetworkError glpi_status=%s", net_status)
        raise HTTPException(status_code=status, detail="Falha de comunicação com serviço GLPI.")
    except GLPISearchError as e:
        status = e.status_code or 502
        logger.error("endpoint=/tickets-novos itemtype=Ticket error=GLPISearchError glpi_status=%s", status)
        raise HTTPException(status_code=status, detail="Erro ao consultar dados do GLPI.")
