from typing import Optional

from pydantic import BaseModel, ConfigDict


class TechnicianRankingItem(BaseModel):
    """Define a estrutura de um item no resultado do ranking de técnicos."""
    tecnico: str
    tickets: int
    nivel: str
    # Pydantic v2: substitui class-based Config por ConfigDict
    model_config = ConfigDict(from_attributes=True)


class GeneralStats(BaseModel):
    """Define a estrutura para as estatísticas gerais de tickets."""
    novos: int
    em_progresso: int
    pendentes: int
    resolvidos: int


class LevelStatsDetail(BaseModel):
    """Define a estrutura detalhada de status para um único nível."""
    novos: int
    em_progresso: int
    pendentes: int
    resolvidos: int
    total: int


class LevelStats(BaseModel):
    """Define a estrutura para as estatísticas de tickets por nível."""
    N1: LevelStatsDetail
    N2: LevelStatsDetail
    N3: LevelStatsDetail
    N4: LevelStatsDetail


class NewTicketItem(BaseModel):
    """Define a estrutura de um item na lista de tickets novos."""
    id: Optional[int] = None
    titulo: str
    solicitante: str
    data: str
