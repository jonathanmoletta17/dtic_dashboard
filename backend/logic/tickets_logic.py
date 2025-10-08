"""
Módulo de lógica de negócios para funcionalidades relacionadas a tickets.
"""

from typing import Any, Dict, List

import backend.glpi_client as glpi_client
from backend.logic.glpi_constants import FIELD_CREATED, FIELD_STATUS, FIELD_TECH, STATUS


def get_new_tickets(api_url: str, session_headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Busca os 10 tickets mais recentes com status 'Novo'.
    A lógica de resolução de nome de solicitante foi simplificada para esta versão.
    """
    criteria = [{"field": str(FIELD_STATUS), "searchtype": "equals", "value": str(STATUS["NEW"])}]  # Status = Novo
# Campos: Título(1), ID(2), Requisitante(4), Técnico(FIELD_TECH), Recipiente(6), Último Atualizador(71), Data de Criação(FIELD_CREATED)
    forcedisplay = ["1", "2", "4", str(FIELD_TECH), "6", "71", str(FIELD_CREATED)]

    tickets = glpi_client.search_paginated(
        session_headers, api_url, "Ticket", criteria, forcedisplay=forcedisplay,
        uid_cols=False, range_step=50
    )

    if not tickets:
        return []

    # Ordena por ID (campo '2') em ordem decrescente para obter os mais recentes
    tickets_sorted = sorted(tickets, key=lambda x: x.get("2", 0), reverse=True)[:10]

    # Otimização: Coletar IDs de requisitantes (campo 4) para buscar nomes em lote
    def get_first_numeric_id(value):
        if value is None:
            return None
        # Campo 4 pode ser string numérica ou lista de IDs
        if isinstance(value, list):
            for v in value:
                v_str = str(v)
                if v_str.isdigit():
                    return int(v_str)
            return None
        # Caso seja string/numero único
        v_str = str(value)
        return int(v_str) if v_str.isdigit() else None

    requester_ids = []
    for ticket in tickets_sorted:
        rid = get_first_numeric_id(ticket.get("4"))
        if isinstance(rid, int):
            requester_ids.append(rid)

    user_names_map = glpi_client.get_user_names_in_batch_with_fallback(session_headers, api_url, requester_ids)

    result = []
    for ticket in tickets_sorted:
        ticket_id = ticket.get("2")
        titulo = ticket.get("1", "Sem título")
        data_ticket = ticket.get(str(FIELD_CREATED))
        
        try:
            from datetime import datetime
            dt = datetime.strptime(data_ticket, "%Y-%m-%d %H:%M:%S")
            data_formatada = dt.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            data_formatada = data_ticket[:10] if data_ticket else ""
        
        # Lógica OTIMIZADA para encontrar o nome do solicitante
        solicitante = "Não informado"
        requester_id = get_first_numeric_id(ticket.get("4"))
        if isinstance(requester_id, int) and requester_id in user_names_map:
            solicitante = user_names_map[requester_id]

        result.append({
            "id": ticket_id,
            "titulo": titulo,
            "solicitante": solicitante,
            "data": data_formatada
        })

    return result
