"""
Módulo de lógica de negócios para geração de métricas de estatísticas do GLPI.
"""

from typing import Dict, Any

# Importa o cliente GLPI para ser usado pelas funções de lógica
import glpi_client

def generate_level_stats(api_url: str, session_headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Busca todos os tickets por grupo e status, e processa os dados em Python.
    Esta é a única fonte da verdade para as contagens de tickets.
    """
"""
Módulo de lógica de negócios para geração de métricas de estatísticas do GLPI.
"""

from typing import Dict, Any
from collections import Counter

def generate_level_stats(api_url: str, session_headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Busca tickets por nível usando a abordagem final e baseada em evidências:
    1. Busca TODAS as associações de Group_User.
    2. Filtra e mapeia os usuários para os grupos de interesse em Python.
    3. Conta os tickets por status para os usuários de cada grupo.
    """
    try:
        group_mapping = { 89: "N1", 90: "N2", 91: "N3", 92: "N4" }
        status_mapping = { 1: "novos", 2: "em_progresso", 3: "pendentes", 6: "resolvidos" }
        
        # 1. Prepara a estrutura de dados para a resposta
        level_stats = { level_name: { status_name: 0 for status_name in status_mapping.values() } for level_name in group_mapping.values() }
        for stats in level_stats.values():
            stats['total'] = 0

        print("🔍 Estratégia Final: Lendo todos os Group_User e filtrando em Python...")
        # Passo A: Buscar TODAS as associações de usuário-grupo
        # CORREÇÃO FINAL: Usando IDs numéricos que funcionam com a API GLPI
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
            forcedisplay=['users_id_tech', 'status'] # CORRIGIDO: usando nomes de campos
        )
        print(f"   - {len(all_assigned_tickets)} tickets encontrados para esses usuários.")

        # Passo D: Processar e agregar os resultados em Python
        for ticket in all_assigned_tickets:
            # CORREÇÃO: Acessando pelos nomes de campos corretos
            assigned_user_id = ticket.get('users_id_tech')
            status_id = ticket.get('status')

            if assigned_user_id in user_to_level_map and status_id in status_mapping:
                level_name = user_to_level_map[assigned_user_id]
                status_name = status_mapping[status_id]
                
                level_stats[level_name][status_name] += 1
                level_stats[level_name]['total'] += 1

        return level_stats

    except Exception as e:
        print(f"❌ Erro em generate_level_stats: {e}")
        raise e