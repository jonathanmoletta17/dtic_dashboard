from typing import Any, Dict

from backend.logic.glpi_constants import FIELD_CREATED, FIELD_STATUS


def _next_criteria_index(params: Dict[str, Any]) -> int:
    max_idx = -1
    for k in params.keys():
        if k.startswith("criteria["):
            try:
                idx_str = k.split("[")[1].split("]")[0]
                idx = int(idx_str)
                if idx > max_idx:
                    max_idx = idx
            except Exception:
                continue
    return max_idx + 1


def _normalize_end(fim: str) -> str:
    return fim if len(fim) > 10 else f"{fim} 23:59:59"


def add_date_range(params: Dict[str, Any], inicio: str, fim: str) -> Dict[str, Any]:
    """Adiciona critérios de intervalo de data usando sempre FIELD_CREATED (15).

    Inclui link=AND caso já existam critérios anteriores.
    """
    idx = _next_criteria_index(params)
    fim_value = _normalize_end(fim)

    # Primeiro critério de data (>= inicio)
    if idx > 0:
        params[f"criteria[{idx}][link]"] = "AND"
    params[f"criteria[{idx}][field]"] = str(FIELD_CREATED)
    params[f"criteria[{idx}][searchtype]"] = "morethan"
    params[f"criteria[{idx}][value]"] = inicio
    idx += 1

    # Segundo critério de data (<= fim)
    params[f"criteria[{idx}][link]"] = "AND"
    params[f"criteria[{idx}][field]"] = str(FIELD_CREATED)
    params[f"criteria[{idx}][searchtype]"] = "lessthan"
    params[f"criteria[{idx}][value]"] = fim_value
    return params


def add_status(params: Dict[str, Any], status_id: int) -> Dict[str, Any]:
    """Adiciona critério de status (FIELD_STATUS) equals."""
    idx = _next_criteria_index(params)
    if idx > 0:
        params[f"criteria[{idx}][link]"] = "AND"
    params[f"criteria[{idx}][field]"] = str(FIELD_STATUS)
    params[f"criteria[{idx}][searchtype]"] = "equals"
    params[f"criteria[{idx}][value]"] = str(status_id)
    return params