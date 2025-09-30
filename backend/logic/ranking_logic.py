"""
Módulo de lógica de negócios para geração do ranking de técnicos.
Implementação correta baseada no ranking_refactored.py validado.
"""

import requests
from collections import Counter
from typing import Dict, List, Any

# A autenticação será feita no nível da API (router) e injetada aqui.
from glpi_client import search_paginated

# O ID do grupo é uma configuração de lógica de negócio, então pode ficar aqui.
TECHNICIAN_GROUP_ID = 17  # ID do grupo pai 'CC-SE-SUBADM-DTIC'


def get_group_members(headers: Dict[str, str], api_url: str, parent_group_id: int) -> List[int]:
    """
    Busca IDs de técnicos ativos que pertencem a um grupo pai ou a seus subgrupos.
    Utiliza uma única chamada de API para eficiência.
    """
    # Critérios de busca:
    # 1. O usuário deve pertencer ao grupo pai (ou subgrupos, com 'under')
    # 2. O usuário deve estar ativo (is_active = 1)
    criteria = [
        {
            'field': 13,       # Campo para "Grupos"
            'searchtype': 'under',
            'value': parent_group_id
        },
        {
            'field': 8,        # Campo para "Ativo" (is_active)
            'searchtype': 'equals',
            'value': '1'
        }
    ]
    
    # Busca os usuários que correspondem aos critérios
    active_users = search_paginated(
        headers,
        api_url,
        "User",
        criteria=criteria,
        uid_cols=False,
        forcedisplay=['2']  # Queremos apenas o ID do usuário, que é o campo 2
    )
    
    # Extrai os IDs dos resultados
    user_ids = [int(user['2']) for user in active_users if '2' in user]
    
    return user_ids


def get_user_name(headers: Dict[str, str], api_url: str, user_id: int) -> str:
    """Busca o nome completo de um usuário pelo ID."""
    try:
        user_url = f"{api_url}/User/{user_id}"
        response = requests.get(user_url, headers=headers)
        response.raise_for_status()
        user_data = response.json()
        
        # A API pode retornar uma lista mesmo para um único ID
        if isinstance(user_data, list) and user_data:
            user_data = user_data[0]
        
        first_name = user_data.get('firstname', '')
        last_name = user_data.get('realname', '')
        
        return f"{first_name} {last_name}".strip()
        
    except requests.exceptions.RequestException:
        return f"Usuário ID {user_id} (Não Encontrado)"
    except (IndexError, KeyError):
        return f"Usuário ID {user_id} (Dados Incompletos)"


def generate_technician_ranking(api_url: str, session_headers: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Gera o ranking de técnicos baseado na lógica correta e validada.
    Recebe a URL da API e os headers de sessão já autenticados.
    
    Returns:
        List[Dict]: Lista de dicionários com formato:
        [{"tecnico": "Nome do Técnico", "tickets": 123, "nivel": "N/A"}, ...]
        Ordenada por número de tickets (decrescente).
    """
    try:
        # A autenticação agora é feita fora desta função.
        # 1. Obter a lista de todos os técnicos ativos nos grupos corretos
        active_technician_ids = get_group_members(session_headers, api_url, TECHNICIAN_GROUP_ID)
        active_technician_set = set(active_technician_ids)

        if not active_technician_set:
            return []

        # 2. Buscar todos os tickets usando a busca paginada robusta
        all_tickets = search_paginated(
            headers=session_headers,
            api_url=api_url,
            itemtype="Ticket",
            forcedisplay=['5'],  # Campo 'Técnico' (users_id_tech)
            uid_cols=False
        )

        # 3. Contar tickets por técnico
        # O ID do técnico responsável está na chave '5' e pode ser uma lista
        technician_ids_with_tickets = []
        for ticket in all_tickets:
            recipient_data = ticket.get('5')
            if not recipient_data:
                continue

            recipients = recipient_data if isinstance(recipient_data, list) else [recipient_data]
            
            for tech_id in recipients:
                try:
                    tech_id_int = int(tech_id)
                    if tech_id_int in active_technician_set:
                        technician_ids_with_tickets.append(tech_id_int)
                except (ValueError, TypeError):
                    continue

        # Contar ocorrências
        ticket_counts = Counter(technician_ids_with_tickets)

        if not ticket_counts:
            return []

        # 4. Montar o ranking com nomes
        ranking_data = []
        for tech_id, count in ticket_counts.items():
            tech_name = get_user_name(session_headers, api_url, tech_id)
            ranking_data.append({
                "tecnico": tech_name,
                "tickets": count,
                "nivel": "N/A"  # Mantém compatibilidade com formato esperado pelo frontend
            })

        # 5. Ordenar por número de tickets (decrescente)
        ranking_data.sort(key=lambda x: x["tickets"], reverse=True)

        return ranking_data

    except Exception as e:
        print(f"❌ Erro ao gerar ranking: {e}")
        # Lançar a exceção para que a camada da API possa tratá-la
        raise e