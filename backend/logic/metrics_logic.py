"""
Módulo de lógica de negócios para geração de métricas de estatísticas do GLPI.
"""

from typing import Dict, Any
from collections import Counter
import requests

# Importa o cliente GLPI para ser usado pelas funções de lógica
import glpi_client

def generate_level_stats(api_url: str, session_headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Busca tickets por nível usando a abordagem final e baseada em evidências:
    1. Busca TODAS as associações de Group_User.
    2. Filtra e mapeia os usuários para os grupos de interesse em Python.
    3. Conta os tickets por status para os usuários de cada grupo.
    """
    try:
        group_mapping = { 89: "N1", 90: "N2", 91: "N3", 92: "N4" }

        # Grupos de status conforme GLPI (campo 12) e agregação do dashboard
        status_groups = {
            "novos": {1},
            "em_progresso": {2, 3},
            "pendentes": {4},
            "resolvidos": {5, 6},
        }
        
        # 1. Prepara a estrutura de dados para a resposta
        level_stats = { level_name: { key: 0 for key in status_groups.keys() } for level_name in group_mapping.values() }
        for stats in level_stats.values():
            stats['total'] = 0

        print("🔍 Estratégia Final: Lendo todos os Group_User e filtrando em Python...")
        # Passo A: Buscar TODAS as associações de usuário-grupo
        # Usando IDs numéricos que funcionam com a API GLPI
        all_group_user_links = glpi_client.search_paginated(
            session_headers, api_url, "Group_User", 
            forcedisplay=['2', '3'] # IDs numéricos: 2=users_id, 3=groups_id
        )

        # Passo B: Mapear usuários para os níveis de interesse
        user_to_level_map = {}
        for link in all_group_user_links:
            # Acessando pelos IDs numéricos que funcionam
            user_id = link.get('2')
            group_id = link.get('3')
            if user_id and group_id in group_mapping:
                user_to_level_map[user_id] = group_mapping[group_id]
        
        print(f"   - {len(user_to_level_map)} usuários mapeados para os níveis de interesse.")

        # Passo C: Buscar todos os tickets que estão atribuídos a esses usuários
        if not user_to_level_map:
            return level_stats # Retorna zerado se não há usuários nos grupos

        ticket_criteria = []
        user_ids = list(user_to_level_map.keys())
        for i, user_id in enumerate(user_ids):
            link_type = "OR" if i < len(user_ids) - 1 else ""
            # Campo 5 em Ticket é 'users_id_tech' (Técnico encarregado)
            ticket_criteria.append({"field": "5", "searchtype": "equals", "value": str(user_id), "link": link_type})

        all_assigned_tickets = glpi_client.search_paginated(
            session_headers, api_url, "Ticket",
            criteria=ticket_criteria,
            forcedisplay=['users_id_tech', 'status'] # usando nomes de campos
        )
        print(f"   - {len(all_assigned_tickets)} tickets encontrados para esses usuários.")

        # Passo D: Processar e agregar os resultados em Python
        for ticket in all_assigned_tickets:
            assigned_user_id = ticket.get('users_id_tech')
            status_id = ticket.get('status')

            if assigned_user_id in user_to_level_map and isinstance(status_id, int):
                level_name = user_to_level_map[assigned_user_id]

                # Descobrir qual grupo de status pertence
                for group_name, ids in status_groups.items():
                    if status_id in ids:
                        level_stats[level_name][group_name] += 1
                        level_stats[level_name]['total'] += 1
                        break

        return level_stats

    except Exception as e:
        print(f"❌ Erro em generate_level_stats: {e}")
        raise e


def generate_general_stats(api_url: str, session_headers: Dict[str, str]) -> Dict[str, int]:
    """
    Conta tickets diretamente pelo Status (campo 12) usando /search/Ticket
    e retorna agregados conforme o dashboard:
      - novos: 1
      - em_progresso: 2 + 3
      - pendentes: 4
      - resolvidos: 5 + 6
    """
    try:
        def count_status(status_id: int) -> int:
            url = f"{api_url}/search/Ticket"
            params = {
                "uid_cols": "1",
                "criteria[0][field]": "12",
                "criteria[0][searchtype]": "equals",
                "criteria[0][value]": str(status_id),
                "range": "0-0",
            }
            resp = requests.get(url, headers=session_headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            try:
                return int(data.get("totalcount", 0))
            except (TypeError, ValueError):
                return 0

        novos = count_status(1)
        em_progresso = count_status(2) + count_status(3)
        pendentes = count_status(4)
        resolvidos = count_status(5) + count_status(6)

        return {
            "novos": novos,
            "em_progresso": em_progresso,
            "pendentes": pendentes,
            "resolvidos": resolvidos,
        }

    except Exception as e:
        print(f"❌ Erro em generate_general_stats: {e}")
        raise e