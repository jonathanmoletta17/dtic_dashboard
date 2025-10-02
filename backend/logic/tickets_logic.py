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
        # Campos: Título(1), ID(2), Requisitante(4), Técnico(5), Recipiente(6), Último Atualizador(71), Data de Criação(15)
        forcedisplay = ["1", "2", "4", "5", "6", "71", "15"]
        
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
                    try:
                        v_str = str(v)
                        if v_str.isdigit():
                            return int(v_str)
                    except Exception:
                        continue
                return None
            # Caso seja string/numero único
            try:
                v_str = str(value)
                if v_str.isdigit():
                    return int(v_str)
            except Exception:
                pass
            return None

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
            data_ticket = ticket.get("15")
            
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

    except Exception as e:
        print(f"❌ Erro ao buscar tickets novos: {e}")
        raise e
