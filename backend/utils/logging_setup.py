import logging


def configure_logging(json: bool = False) -> None:
    """
    Configura logging global simples para o backend.
    - Formato linha simples com timestamp, nível e módulo.
    - Evita múltiplos handlers duplicados.
    - JSON opcional não implementado para manter simplicidade.
    """
    if logging.getLogger().handlers:
        # Já configurado; evita duplicação
        return
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt)


def format_range(inicio: str | None, fim: str | None) -> str:
    return f"{inicio or ''}..{fim or ''}"