"""
Módulo de lógica de negócios para geração de métricas de estatísticas do GLPI.
Implementação direta usando filtros de busca na API GLPI.
"""

from typing import Dict, Any, Tuple
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter


def generate_level_stats(
    api_url: str,
    session_headers: Dict[str, str],
    inicio: str | None = None,
    fim: str | None = None,
    campo_data: int = 15,
) -> Dict[str, Any]:
    """
    Conta tickets por nível usando filtros diretos na API GLPI:
    - Hierarquia (campo 8) com searchtype=contains para "N1".."N4"
    - Status (campo 12) com searchtype=equals para IDs 1..6

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

            # criteria 0: nível (campo 8)
            index = 0
            params[f"criteria[{index}][field]"] = "8"
            params[f"criteria[{index}][searchtype]"] = "contains"
            params[f"criteria[{index}][value]"] = level_value
            index += 1

            # critérios de data (opcionais)
            if inicio and fim:
                fim_value = fim if len(fim) > 10 else f"{fim} 23:59:59"
                params[f"criteria[{index}][link]"] = "AND"
                params[f"criteria[{index}][field]"] = str(campo_data)
                params[f"criteria[{index}][searchtype]"] = "morethan"
                params[f"criteria[{index}][value]"] = inicio
                index += 1

                params[f"criteria[{index}][link]"] = "AND"
                params[f"criteria[{index}][field]"] = str(campo_data)
                params[f"criteria[{index}][searchtype]"] = "lessthan"
                params[f"criteria[{index}][value]"] = fim_value
                index += 1

            # critério de status (campo 12)
            params[f"criteria[{index}][link]"] = "AND"
            params[f"criteria[{index}][field]"] = "12"
            params[f"criteria[{index}][searchtype]"] = "equals"
            params[f"criteria[{index}][value]"] = str(status_id)
            try:
                resp = session.get(url, headers=session_headers, params=params, timeout=(2, 4))
                resp.raise_for_status()
                data = resp.json()
                try:
                    count = int(data.get("totalcount", 0))
                except (TypeError, ValueError):
                    count = 0
                return level_value, status_id, count
            except requests.exceptions.RequestException:
                return level_value, status_id, 0

        levels = ["N1", "N2", "N3", "N4"]
        statuses = [1, 2, 3, 4, 5, 6]
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
                if st == 1:
                    level_stats[lvl]["novos"] += cnt
                elif st in (2, 3):
                    level_stats[lvl]["em_progresso"] += cnt
                elif st == 4:
                    level_stats[lvl]["pendentes"] += cnt
                elif st in (5, 6):
                    level_stats[lvl]["resolvidos"] += cnt
                # Atualiza total incrementalmente
                level_stats[lvl]["total"] = (
                    level_stats[lvl]["novos"] +
                    level_stats[lvl]["em_progresso"] +
                    level_stats[lvl]["pendentes"] +
                    level_stats[lvl]["resolvidos"]
                )

        return level_stats

    except Exception as e:
        print(f"❌ Erro em generate_level_stats: {e}")
        raise e


def generate_general_stats(
    api_url: str,
    session_headers: Dict[str, str],
    inicio: str | None = None,
    fim: str | None = None,
    campo_data: int = 15,
) -> Dict[str, int]:
    """
    Conta tickets diretamente pelo Status (campo 12) usando /search/Ticket
    e retorna agregados conforme o dashboard:
      - novos: 1
      - em_progresso: 2 + 3
      - pendentes: 4
      - resolvidos: 5 + 6
    Se "inicio" e "fim" forem fornecidos, aplica filtro de intervalo de datas
    usando o campo especificado em "campo_data" (padrão 15 = data de criação).
    """
    try:
        def count_status(status_id: int) -> int:
            url = f"{api_url}/search/Ticket"
            params: Dict[str, Any] = {
                "uid_cols": "1",
                "range": "0-0",
            }

            index = 0
            if inicio and fim:
                fim_value = fim if len(fim) > 10 else f"{fim} 23:59:59"
                params[f"criteria[{index}][field]"] = str(campo_data)
                params[f"criteria[{index}][searchtype]"] = "morethan"
                params[f"criteria[{index}][value]"] = inicio
                index += 1
                params[f"criteria[{index}][link]"] = "AND"
                params[f"criteria[{index}][field]"] = str(campo_data)
                params[f"criteria[{index}][searchtype]"] = "lessthan"
                params[f"criteria[{index}][value]"] = fim_value
                index += 1

            if index > 0:
                params[f"criteria[{index}][link]"] = "AND"
            params[f"criteria[{index}][field]"] = "12"
            params[f"criteria[{index}][searchtype]"] = "equals"
            params[f"criteria[{index}][value]"] = str(status_id)
            resp = requests.get(url, headers=session_headers, params=params, timeout=(2, 4))
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