"""
Script de Diagnóstico: Endpoint /api/v1/ranking-tecnicos retornando []

Objetivo: Validar, de forma isolada e sem alterar produção, três pontos críticos:
1) Carregamento de variáveis de ambiente (.env de backend) e identificação do grupo.
2) Autenticação na API GLPI.
3) Busca de membros ativos do grupo (under -> fallback equals), reportando URL, parâmetros e totalcount.
4) Contagem de tickets para um técnico de amostra via campo '5' com range 0-0.

Saída: imprime detalhes das requisições e resultados para montar o diagnóstico.
"""

import os
import sys
from typing import Dict, Any, List

import requests
from dotenv import load_dotenv


# Ajusta sys.path para importar módulos do backend sem alterar produção
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

import backend.glpi_client as glpi_client


def load_env_from_backend() -> Dict[str, str]:
    dotenv_path = os.path.join(BACKEND_DIR, ".env")
    load_dotenv(dotenv_path=dotenv_path)
    return {
        "API_URL": os.getenv("API_URL", ""),
        "APP_TOKEN": os.getenv("APP_TOKEN", ""),
        "USER_TOKEN": os.getenv("USER_TOKEN", ""),
        "RANKING_TECHNICIAN_PARENT_GROUP_ID": os.getenv("RANKING_TECHNICIAN_PARENT_GROUP_ID", "17"),
    }


def print_request_details(url: str, params: Dict[str, Any]) -> None:
    print("== Requisição GLPI ==")
    print(f"URL: {url}")
    print("Parâmetros:")
    for k in sorted(params.keys()):
        print(f"  - {k}: {params[k]}")


def diagnose_group_members(headers: Dict[str, str], api_url: str, parent_group_id: int) -> List[int]:
    """Replica a lógica de get_group_members, reportando cada etapa."""
    search_url = f"{api_url}/search/User"
    base_params = {
        'uid_cols': '0',
        'forcedisplay[0]': '2',  # ID do usuário
        'criteria[0][field]': 13,
        'criteria[0][searchtype]': 'under',
        'criteria[0][value]': str(parent_group_id),
        'criteria[1][field]': 8,
        'criteria[1][searchtype]': 'equals',
        'criteria[1][value]': '1',
    }

    # Etapa 1: contar com 'under'
    params_count = dict(base_params)
    params_count['range'] = '0-0'
    print("\n[Passo 1] Contagem de membros ativos do grupo (searchtype=under)")
    print_request_details(search_url, params_count)
    try:
        resp_count = requests.get(search_url, headers=headers, params=params_count, timeout=(3, 6))
        resp_count.raise_for_status()
        data_count = resp_count.json()
        total_under = int(data_count.get('totalcount', 0) or 0)
        print(f"totalcount (under): {total_under}")
    except Exception as e:
        print(f"❌ Falha na contagem (under): {e}")
        total_under = 0

    total = total_under

    # Fallback: contar com 'equals' se under não retornou
    if total_under <= 0:
        params_count_eq = dict(base_params)
        params_count_eq['criteria[0][searchtype]'] = 'equals'
        params_count_eq['range'] = '0-0'
        print("\n[Passo 1b] Contagem de membros ativos do grupo (fallback searchtype=equals)")
        print_request_details(search_url, params_count_eq)
        try:
            resp_count_eq = requests.get(search_url, headers=headers, params=params_count_eq, timeout=(3, 6))
            resp_count_eq.raise_for_status()
            data_count_eq = resp_count_eq.json()
            total_eq = int(data_count_eq.get('totalcount', 0) or 0)
            print(f"totalcount (equals): {total_eq}")
            total = total_eq
        except Exception as e:
            print(f"❌ Falha na contagem (equals): {e}")
            total = 0

    # Etapa 2: buscar linhas se houver total
    if total <= 0:
        print(f"⚠️ Nenhum membro ativo encontrado para o grupo ID {parent_group_id}.")
        return []

    end_index = min(total - 1, 199)  # limita a 200 registros para diagnóstico
    params_rows = dict(base_params)
    params_rows['range'] = f'0-{end_index}'
    print("\n[Passo 2] Busca de linhas (under)")
    print_request_details(search_url, params_rows)
    users: List[Dict[str, Any]] = []
    try:
        resp_rows = requests.get(search_url, headers=headers, params=params_rows, timeout=(3, 6))
        resp_rows.raise_for_status()
        data_rows = resp_rows.json()
        users = data_rows.get('data', []) or []
        print(f"Linhas retornadas (under): {len(users)}")
        if users:
            print(f"Campos do primeiro registro (under): {sorted(list(users[0].keys()))}")
    except Exception as e:
        print(f"❌ Falha na busca de linhas (under): {e}")

    if not users:
        params_rows_eq = dict(base_params)
        params_rows_eq['criteria[0][searchtype]'] = 'equals'
        params_rows_eq['range'] = f'0-{end_index}'
        print("\n[Passo 2b] Busca de linhas (fallback equals)")
        print_request_details(search_url, params_rows_eq)
        try:
            resp_rows_eq = requests.get(search_url, headers=headers, params=params_rows_eq, timeout=(3, 6))
            resp_rows_eq.raise_for_status()
            data_rows_eq = resp_rows_eq.json()
            users = data_rows_eq.get('data', []) or []
            print(f"Linhas retornadas (equals): {len(users)}")
            if users:
                print(f"Campos do primeiro registro (equals): {sorted(list(users[0].keys()))}")
        except Exception as e:
            print(f"❌ Falha na busca de linhas (equals): {e}")

    ids: List[int] = []
    for u in users:
        id_val = u.get('2') or u.get('User.id') or u.get('id')
        try:
            if id_val is not None:
                ids.append(int(id_val))
        except (TypeError, ValueError):
            continue
    print(f"IDs (amostra): {ids[:10]}{' ...' if len(ids) > 10 else ''}")
    return ids


def count_tickets_for_one(headers: Dict[str, str], api_url: str, tech_id: int) -> int:
    """Simula count_tickets_by_tech_parallel para um único técnico (field '5')."""
    search_url = f"{api_url}/search/Ticket"
    params = {
        "criteria[0][field]": "5",
        "criteria[0][searchtype]": "equals",
        "criteria[0][value]": str(tech_id),
        "range": "0-0",
    }
    print("\n[Passo 3] Contagem de tickets por técnico (field=5)")
    print_request_details(search_url, params)
    try:
        resp = requests.get(search_url, headers=headers, params=params, timeout=(3, 6))
        resp.raise_for_status()
        data = resp.json()
        total = int(data.get("totalcount", 0) or 0)
        print(f"totalcount (tickets para técnico {tech_id}): {total}")
        return total
    except Exception as e:
        print(f"❌ Falha na contagem de tickets para técnico {tech_id}: {e}")
        return 0


def main() -> int:
    env = load_env_from_backend()
    api_url = env["API_URL"]
    app_token = env["APP_TOKEN"]
    user_token = env["USER_TOKEN"]
    group_id_str = env["RANKING_TECHNICIAN_PARENT_GROUP_ID"]
    try:
        group_id = int(group_id_str)
    except ValueError:
        group_id = 17

    print("== Configurações ==")
    print(f"API_URL: {api_url}")
    print(f"RANKING_TECHNICIAN_PARENT_GROUP_ID: {group_id}")

    if not all([api_url, app_token, user_token]):
        print("❌ Variáveis de ambiente ausentes: API_URL, APP_TOKEN, USER_TOKEN (backend/.env)")
        return 1

    # Autenticação
    print("\n[Autenticação] Iniciando sessão GLPI...")
    try:
        headers = glpi_client.authenticate(api_url, app_token, user_token)
        print("✅ Autenticação e configuração de entidade realizadas!")
    except Exception as e:
        print(f"❌ Falha na autenticação GLPI: {e}")
        return 1

    # Diagnóstico do grupo
    ids = diagnose_group_members(headers, api_url, group_id)
    if not ids:
        print("\nResultado: Nenhum membro ativo encontrado no grupo. O endpoint provavelmente retorna [].")
        return 0

    # Contagem de tickets para técnico de amostra
    sample_id = ids[0]
    count_tickets_for_one(headers, api_url, sample_id)
    print("\n✅ Diagnóstico concluído.")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())