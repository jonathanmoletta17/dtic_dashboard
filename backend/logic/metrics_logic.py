"""
Módulo de lógica de negócios para geração de métricas de estatísticas do GLPI.
Implementação direta usando filtros de busca na API GLPI.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Tuple

import requests
from requests.adapters import HTTPAdapter

from backend.logic.criteria_helpers import add_date_range, add_status
from backend.logic.errors import GLPIAuthError, GLPINetworkError, GLPISearchError
from backend.logic.glpi_constants import (
    FIELD_LEVEL,
    STATUS,
)


def generate_level_stats(
    api_url: str,
    session_headers: Dict[str, str],
    inicio: str | None = None,
    fim: str | None = None,
) -> Dict[str, Any]:
    """
    Conta tickets por nível usando filtros diretos na API GLPI:
    - Hierarquia (FIELD_LEVEL) com searchtype=contains para "N1".."N4"
    - Status (FIELD_STATUS) com searchtype=equals para IDs definidos em STATUS

    Retorna um dicionário com as chaves N1..N4 nas agregações:
    { "N1": {"novos": int, "em_progresso": int, "pendentes": int, "resolvidos": int, "total": int }, ... }
    """
    try:
        def fetch_count(session: requests.Session, level_value: str, status_id: int) -> Tuple[str, int, int]:
            url = f"{api_url}/search/Ticket"
            params: Dict[str, Any] = {
                "uid_cols": "1",
                "range": "0-0",
            }

            # criteria 0: nível (FIELD_LEVEL)
            index = 0
            params[f"criteria[{index}][field]"] = str(FIELD_LEVEL)
            params[f"criteria[{index}][searchtype]"] = "contains"
            params[f"criteria[{index}][value]"] = level_value
            index += 1

            # critérios de data opcionais (FIELD_CREATED) e status (FIELD_STATUS)
            if inicio and fim:
                add_date_range(params, inicio, fim)
            add_status(params, status_id)
            try:
                resp = session.get(url, headers=session_headers, params=params, timeout=(2, 4))
                resp.raise_for_status()
                data = resp.json()
                try:
                    count = int(data.get("totalcount", 0))
                except (TypeError, ValueError):
                    count = 0
                return level_value, status_id, count
            except requests.exceptions.Timeout:
                raise GLPINetworkError("Timeout ao buscar métricas por nível", timeout=True)
            except requests.exceptions.HTTPError as e:
                status = getattr(e.response, 'status_code', None)
                if status in (401, 403):
                    raise GLPIAuthError("Falha de autenticação em métricas por nível", status_code=status)
                raise GLPISearchError(f"Erro HTTP em métricas por nível (status={status})", status_code=status)
            except requests.exceptions.RequestException:
                raise GLPINetworkError("Falha de rede ao buscar métricas por nível")

        levels = ["N1", "N2", "N3", "N4"]
        statuses = [
            STATUS["NEW"],
            STATUS["ASSIGNED"],
            STATUS["PLANNED"],
            STATUS["IN_PROGRESS"],
            STATUS["SOLVED"],
            STATUS["CLOSED"],
        ]
        level_stats = {lvl: {"novos": 0, "em_progresso": 0, "pendentes": 0, "resolvidos": 0, "total": 0} for lvl in levels}

        session = requests.Session()
        adapter = HTTPAdapter(pool_connections=20, pool_maxsize=20)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        with ThreadPoolExecutor(max_workers=12) as executor:
            futures = []
            for lvl in levels:
                for st in statuses:
                    futures.append(executor.submit(fetch_count, session, lvl, st))
            for fut in as_completed(futures):
                lvl, st, cnt = fut.result()
                if st == STATUS["NEW"]:
                    level_stats[lvl]["novos"] += cnt
                elif st in (STATUS["ASSIGNED"], STATUS["PLANNED"]):
                    level_stats[lvl]["em_progresso"] += cnt
                elif st == STATUS["IN_PROGRESS"]:
                    level_stats[lvl]["pendentes"] += cnt
                elif st in (STATUS["SOLVED"], STATUS["CLOSED"]):
                    level_stats[lvl]["resolvidos"] += cnt
                # Atualiza total incrementalmente
                level_stats[lvl]["total"] = (
                    level_stats[lvl]["novos"] +
                    level_stats[lvl]["em_progresso"] +
                    level_stats[lvl]["pendentes"] +
                    level_stats[lvl]["resolvidos"]
                )

        return level_stats

    except (GLPIAuthError, GLPISearchError, GLPINetworkError):
        # Propaga erros específicos para serem mapeados pelo router
        raise
    except Exception as e:
        # Falhas não previstas na lógica
        raise GLPISearchError("Erro interno na lógica de métricas por nível") from e


def generate_general_stats(
    api_url: str,
    session_headers: Dict[str, str],
    inicio: str | None = None,
    fim: str | None = None,
) -> Dict[str, int]:
    """
    Conta tickets diretamente pelo Status (FIELD_STATUS) usando /search/Ticket
    e retorna agregados conforme o dashboard:
      - novos: STATUS["NEW"]
      - em_progresso: STATUS["ASSIGNED"] + STATUS["PLANNED"]
      - pendentes: STATUS["IN_PROGRESS"]
      - resolvidos: STATUS["SOLVED"] + STATUS["CLOSED"]
    Se "inicio" e "fim" forem fornecidos, aplica filtro de intervalo de datas
    usando sempre a data de criação (FIELD_CREATED).
    """
    try:
        def count_status(status_id: int) -> int:
            url = f"{api_url}/search/Ticket"
            params: Dict[str, Any] = {
                "uid_cols": "1",
                "range": "0-0",
            }

            if inicio and fim:
                add_date_range(params, inicio, fim)
            add_status(params, status_id)
            try:
                resp = requests.get(url, headers=session_headers, params=params, timeout=(2, 4))
                resp.raise_for_status()
                data = resp.json()
                try:
                    return int(data.get("totalcount", 0))
                except (TypeError, ValueError):
                    return 0
            except requests.exceptions.Timeout:
                raise GLPINetworkError("Timeout ao buscar métricas gerais", timeout=True)
            except requests.exceptions.HTTPError as e:
                status = getattr(e.response, 'status_code', None)
                if status in (401, 403):
                    raise GLPIAuthError("Falha de autenticação em métricas gerais", status_code=status)
                raise GLPISearchError(f"Erro HTTP em métricas gerais (status={status})", status_code=status)
            except requests.exceptions.RequestException:
                raise GLPINetworkError("Falha de rede ao buscar métricas gerais")

        novos = count_status(STATUS["NEW"])
        em_progresso = count_status(STATUS["ASSIGNED"]) + count_status(STATUS["PLANNED"])
        pendentes = count_status(STATUS["IN_PROGRESS"])
        resolvidos = count_status(STATUS["SOLVED"]) + count_status(STATUS["CLOSED"])

        return {
            "novos": novos,
            "em_progresso": em_progresso,
            "pendentes": pendentes,
            "resolvidos": resolvidos,
        }

    except (GLPIAuthError, GLPISearchError, GLPINetworkError):
        raise
    except Exception as e:
        raise GLPISearchError("Erro interno na lógica de métricas gerais") from e