"""
Módulo de lógica de negócios para funcionalidades relacionadas a tickets.
"""

import requests
from typing import Dict, List, Any

import glpi_client

def get_new_tickets(api_url: str, session_headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Busca os 10 tickets mais recentes com status 'Novo'.
    A lógica de resolução de nome de solicitante foi simplificada para esta versão.
    """
    try:
        criteria = [{"field": "12", "searchtype": "equals", "value": "1"}]  # Status = Novo
        # Campos: requisitante, técnico, recipiente, último atualizador, data de criação
        forcedisplay = ["4", "5", "6", "71", "15"]
        
        tickets = glpi_client.search_paginated(
            session_headers, api_url, "Ticket", criteria, forcedisplay=forcedisplay,
            uid_cols=False, range_step=50
        )
        
        if not tickets:
            return []
        
        # Ordena por ID (campo '2') em ordem decrescente para obter os mais recentes
        tickets_sorted = sorted(tickets, key=lambda x: x.get("2", 0), reverse=True)[:10]
        
        result = []
        for ticket in tickets_sorted:
            ticket_id = ticket.get("2")
            titulo = ticket.get("1", "Sem título")
            data_ticket = ticket.get("15")
            
            try:
                from datetime import datetime
                dt = datetime.strptime(data_ticket, "%Y-%m-%d %H:%M:%S")
                data_formatada = dt.strftime("%d/%m/%Y %H:%M")
            except (ValueError, TypeError):
                data_formatada = data_ticket[:10] if data_ticket else ""
            
            # Lógica simplificada para encontrar o nome do solicitante
            solicitante = "Não informado"
            requester_id = ticket.get("4") # ID do requisitante
            if requester_id and requester_id != "0":
                try:
                    user_url = f"{api_url}/User/{requester_id}"
                    user_response = requests.get(user_url, headers=session_headers)
                    if user_response.status_code == 200:
                        solicitante = user_response.json().get("name", f"ID:{requester_id}")
                except requests.RequestException:
                    solicitante = f"ID:{requester_id} (Erro de rede)"

            result.append({
                "id": ticket_id,
                "titulo": titulo,
                "solicitante": solicitante,
                "data": data_formatada
            })
        
        return result

    except Exception as e:
        print(f"❌ Erro ao buscar tickets novos: {e}")
        raise e
