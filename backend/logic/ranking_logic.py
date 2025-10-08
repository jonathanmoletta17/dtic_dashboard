"""
Módulo de lógica de negócios para geração do ranking de técnicos.
Implementação correta baseada no ranking_refactored.py validado.
"""

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from typing import Any, Dict, List

import requests
from requests.adapters import HTTPAdapter

# A autenticação será feita no nível da API (router) e injetada aqui.
from backend.glpi_client import get_user_names_in_batch_with_fallback
from backend.logic.errors import GLPIAuthError, GLPINetworkError, GLPISearchError
from backend.logic.glpi_constants import FIELD_GROUP, FIELD_TECH, FIELD_USER_ACTIVE

# O ID do grupo é uma configuração de lógica de negócio, então pode ficar aqui.
TECHNICIAN_GROUP_ID = int(os.environ.get("RANKING_TECHNICIAN_PARENT_GROUP_ID", "17"))  # grupo pai padrão
# Limite padrão de itens no ranking (Top N)
TOP_N_RANKING = 20


def get_group_members(headers: Dict[str, str], api_url: str, parent_group_id: int) -> List[int]:
    """
    Busca IDs de técnicos ativos que pertencem a um grupo pai ou a seus subgrupos.
    Estratégia em duas etapas: primeiro obtém `totalcount` com range 0-0; depois
    faz uma única chamada com `range` ajustado ao total (limitado a 1000).
    """
    search_url = f"{api_url}/search/User"
    base_params = {
        'uid_cols': '0',
        'forcedisplay[0]': '2',  # ID do usuário (GLPI retorna '2'/'User.id')
        'criteria[0][field]': FIELD_GROUP,       # Grupos
        'criteria[0][searchtype]': 'under',
        'criteria[0][value]': str(parent_group_id),
        'criteria[1][field]': FIELD_USER_ACTIVE,        # Ativo
        'criteria[1][searchtype]': 'equals',
        'criteria[1][value]': '1',
    }
    try:
        # Etapa 1: obter apenas o totalcount
        params_count = dict(base_params)
        params_count['range'] = '0-0'
        resp_count = requests.get(search_url, headers=headers, params=params_count, timeout=(3, 6))
        resp_count.raise_for_status()
        data_count = resp_count.json()
        total = int(data_count.get('totalcount', 0) or 0)
        # Se não retornar nada com 'under', tentar com 'equals' (grupo direto)
        if total <= 0:
            params_count_eq = dict(base_params)
            params_count_eq['criteria[0][searchtype]'] = 'equals'
            resp_count_eq = requests.get(search_url, headers=headers, params=params_count_eq, timeout=(3, 6))
            resp_count_eq.raise_for_status()
            data_count_eq = resp_count_eq.json()
            total = int(data_count_eq.get('totalcount', 0) or 0)
            if total <= 0:
                return []

        # Etapa 2: buscar linhas com range ajustado
        end_index = min(total - 1, 999)  # limita a 1000 registros
        params_rows = dict(base_params)
        params_rows['range'] = f'0-{end_index}'
        resp_rows = requests.get(search_url, headers=headers, params=params_rows, timeout=(3, 6))
        resp_rows.raise_for_status()
        data_rows = resp_rows.json()
        rows = data_rows.get('data', []) or []
        # Se com 'under' não vierem linhas, tenta com 'equals'
        if not rows:
            params_rows_eq = dict(base_params)
            params_rows_eq['criteria[0][searchtype]'] = 'equals'
            params_rows_eq['range'] = f'0-{end_index}'
            resp_rows_eq = requests.get(search_url, headers=headers, params=params_rows_eq, timeout=(3, 6))
            resp_rows_eq.raise_for_status()
            data_rows_eq = resp_rows_eq.json()
            rows = data_rows_eq.get('data', []) or []
        ids: List[int] = []
        for row in rows:
            id_val = row.get('2') or row.get('User.id') or row.get('id')
            try:
                if id_val is not None:
                    ids.append(int(id_val))
            except (TypeError, ValueError):
                continue
        return ids
    except requests.exceptions.Timeout:
        raise GLPINetworkError("Timeout ao buscar membros do grupo", timeout=True)
    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, 'status_code', None)
        if status in (401, 403):
            raise GLPIAuthError("Falha de autenticação ao buscar membros do grupo", status_code=status)
        raise GLPISearchError(f"Erro HTTP ao buscar membros do grupo (status={status})", status_code=status)
    except requests.exceptions.RequestException:
        raise GLPINetworkError("Falha de rede ao buscar membros do grupo")


 


def generate_technician_ranking(
    api_url: str,
    session_headers: Dict[str, str],
    inicio: str | None = None,
    fim: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Gera o ranking de técnicos de forma enxuta e preparada para produção.
    Usa apenas membros ativos do grupo técnico e conta pelo campo técnico (FIELD_TECH).

    Returns:
        List[Dict]: Lista com
        [{"tecnico": "Nome do Técnico", "tickets": 123, "nivel": "N/A"}, ...]
        ordenada por número de tickets (decrescente).
    """
    try:
        # 1) Obter técnicos ativos do grupo de produção
        active_technician_ids = get_group_members(session_headers, api_url, TECHNICIAN_GROUP_ID)
        active_technician_set = set(active_technician_ids)
        if not active_technician_set:
            return []

        # 2) Contar tickets por técnico com consulta paralela (campo técnico)
        ticket_counts = count_tickets_by_tech_parallel(
            headers=session_headers,
            api_url=api_url,
            active_technician_set=active_technician_set,
            range_step=1000,
            max_workers=10,
            pool_size=20,
            field_name=str(FIELD_TECH),
            inicio=inicio,
            fim=fim,
        )

        if not ticket_counts:
            # Fallback simples: tenta nome alternativo de campo
            ticket_counts = count_tickets_by_tech_parallel(
                headers=session_headers,
                api_url=api_url,
                active_technician_set=active_technician_set,
                range_step=1000,
                max_workers=10,
                pool_size=20,
                field_name="users_id_assign",
                inicio=inicio,
                fim=fim,
            )
            if not ticket_counts:
                return []

        # 3) Montar ranking com nomes (Top N)
        sorted_counts = sorted(ticket_counts.items(), key=lambda x: x[1], reverse=True)
        top_ids = [tech_id for tech_id, _ in sorted_counts[:TOP_N_RANKING]]
        names_map = get_user_names_in_batch_with_fallback(session_headers, api_url, top_ids)
        ranking_data = []
        for tech_id, count in sorted_counts[:TOP_N_RANKING]:
            tech_name = names_map.get(tech_id, f"Usuário ID {tech_id}")
            ranking_data.append({"tecnico": tech_name, "tickets": count, "nivel": "N/A"})

        return ranking_data

    except (GLPIAuthError, GLPISearchError, GLPINetworkError):
        raise
    except Exception as e:
        raise GLPISearchError("Erro interno na lógica de ranking") from e


def count_tickets_by_tech_parallel(
    headers: Dict[str, str],
    api_url: str,
    active_technician_set: set,
    range_step: int = 1000,
    max_workers: int = 10,
    pool_size: int = 20,
    field_name: str = str(FIELD_TECH),
    inicio: str | None = None,
    fim: str | None = None,
) -> Counter:
    """
    Conta tickets por técnico consultando diretamente o totalcount por users_id_tech.

    Em vez de paginar todos os tickets e somar o campo técnico (FIELD_TECH), fazemos uma
    chamada por técnico: /search/Ticket com criteria field=FIELD_TECH equals tech_id e
    range=0-0 para obter apenas o totalcount. Isso reduz drasticamente o
    número de requisições quando o volume de tickets é alto.

    Args:
        headers: Headers com Session-Token/App-Token.
        api_url: URL base da API GLPI.
        active_technician_set: Conjunto de IDs de técnicos válidos (ativos no grupo).
        range_step: Mantido por compatibilidade (não utilizado nesta estratégia).
        max_workers: Número de workers para paralelização.
        pool_size: Tamanho do pool de conexões HTTP.

    Returns:
        Counter com contagem de tickets por técnico.
    """
    search_url = f"{api_url}/search/Ticket"

    # Sessão com pool de conexões
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    def fetch_count(tech_id: int) -> tuple[int, int]:
        params: Dict[str, Any] = {
            "range": "0-0",
        }
        # Critérios de data opcionais
        if inicio and fim:
            from backend.logic.criteria_helpers import add_date_range
            add_date_range(params, inicio, fim)

        # Filtro de técnico
        # Adiciona após qualquer critério existente
        from backend.logic.criteria_helpers import _next_criteria_index
        idx = _next_criteria_index(params)
        if idx > 0:
            params[f"criteria[{idx}][link]"] = "AND"
        params[f"criteria[{idx}][field]"] = field_name
        params[f"criteria[{idx}][searchtype]"] = "equals"
        params[f"criteria[{idx}][value]"] = str(tech_id)
        try:
            resp = session.get(search_url, headers=headers, params=params, timeout=(2, 4))
            resp.raise_for_status()
            data = resp.json()
            try:
                count = int(data.get("totalcount", 0) or 0)
            except (TypeError, ValueError):
                count = 0
            return tech_id, count
        except requests.exceptions.Timeout:
            raise GLPINetworkError("Timeout ao contar tickets por técnico", timeout=True)
        except requests.exceptions.HTTPError as e:
            status = getattr(e.response, 'status_code', None)
            if status in (401, 403):
                raise GLPIAuthError("Falha de autenticação ao contar tickets por técnico", status_code=status)
            raise GLPISearchError(f"Erro HTTP ao contar tickets por técnico (status={status})", status_code=status)
        except requests.exceptions.RequestException:
            raise GLPINetworkError("Falha de rede ao contar tickets por técnico")

    aggregated = Counter()
    tech_ids = list(active_technician_set)
    if not tech_ids:
        return aggregated

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_count, tid): tid for tid in tech_ids}
        for fut in as_completed(futures):
            tid, cnt = fut.result()
            if cnt > 0:
                aggregated[tid] = cnt

    return aggregated