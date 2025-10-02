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
    Conta tickets por nível usando filtros diretos na API GLPI:
    - Hierarquia (campo 8) com searchtype=contains para "N1".."N4"
    - Status (campo 12) com searchtype=equals para IDs 1..6

    Agregação conforme dashboard:
      - novos: 1
      - em_progresso: 2 + 3
      - pendentes: 4
      - resolvidos: 5 + 6
    """
    try:
        def count_level_status(level_value: str, status_id: int) -> int:
            url = f"{api_url}/search/Ticket"
            params = {
                "uid_cols": "1",
                # Filtro por Hierarquia (campo 8)
                "criteria[0][field]": "8",
                "criteria[0][searchtype]": "contains",
                "criteria[0][value]": level_value,
                # Filtro por Status (campo 12)
                "criteria[1][field]": "12",
                "criteria[1][searchtype]": "equals",
                "criteria[1][value]": str(status_id),
                # Apenas contagem
                "range": "0-0",
            }
            resp = requests.get(url, headers=session_headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            try:
                return int(data.get("totalcount", 0))
            except (TypeError, ValueError):
                return 0

        levels = ["N1", "N2", "N3", "N4"]
        level_stats = {lvl: {"novos": 0, "em_progresso": 0, "pendentes": 0, "resolvidos": 0, "total": 0} for lvl in levels}

        print("🔍 Estratégia por nível: filtrando por campo 8 (Hierarquia) + campo 12 (Status)...")
        for lvl in levels:
            novos = count_level_status(lvl, 1)
            em_prog = count_level_status(lvl, 2) + count_level_status(lvl, 3)
            pend = count_level_status(lvl, 4)
            resol = count_level_status(lvl, 5) + count_level_status(lvl, 6)

            level_stats[lvl]["novos"] = novos
            level_stats[lvl]["em_progresso"] = em_prog
            level_stats[lvl]["pendentes"] = pend
            level_stats[lvl]["resolvidos"] = resol
            level_stats[lvl]["total"] = novos + em_prog + pend + resol

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