// Arquivo de Declaração de Tipos para a API do Backend
// https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html

/** Corresponde ao schema `TechnicianRankingItem` no backend. */
export interface TechnicianRankingItem {
  tecnico: string;
  tickets: number;
  nivel: string;
}

/** Corresponde ao schema `GeneralStats` no backend. */
export interface GeneralStats {
  novos: number;
  em_progresso: number;
  pendentes: number;
  resolvidos: number;
}

/** Define a estrutura detalhada de status para um único nível. */
export interface LevelStatsDetail {
  novos: number;
  em_progresso: number;
  pendentes: number;
  resolvidos: number;
  total: number;
}

/** Corresponde ao schema `LevelStats` no backend. */
export interface LevelStats {
  N1: LevelStatsDetail;
  N2: LevelStatsDetail;
  N3: LevelStatsDetail;
  N4: LevelStatsDetail;
}

/** Corresponde ao schema `NewTicketItem` no backend. */
export interface NewTicketItem {
  id: number | null;
  titulo: string;
  solicitante: string;
  data: string;
}
