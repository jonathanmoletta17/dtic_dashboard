import type {
  GeneralStats,
  LevelStats,
  TechnicianRankingItem,
  NewTicketItem,
} from '../types/api.d';

// O prefixo da nossa API.
// Em desenvolvimento, use proxy do Vite com '/api/v1'.
// Em produção/preview, configure VITE_API_BASE_URL (ex.: 'http://127.0.0.1:8000/api/v1').
const API_BASE_URL = (import.meta as any)?.env?.VITE_API_BASE_URL || '/api/v1';

/**
 * Uma função genérica e reutilizável para buscar dados da nossa API.
 * Ela lida com a chamada de rede, erros e a conversão da resposta para JSON.
 * @param endpoint O caminho do endpoint da API (ex: '/metrics-gerais').
 * @returns Os dados da API, já com o tipo correto.
 */
async function fetchFromAPI<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);

  if (!response.ok) {
    // Tenta extrair uma mensagem de erro mais detalhada do corpo da resposta
    const errorData = await response.json().catch(() => ({
      detail: `Erro de rede: ${response.statusText} ao acessar o endpoint ${endpoint}`,
    }));
    throw new Error(errorData.detail || 'Ocorreu um erro desconhecido na API.');
  }

  return response.json();
}

// Exporta uma função específica para cada endpoint, usando o nosso helper genérico.

export const fetchGeneralStats = (inicio?: string, fim?: string) => {
  const qs = inicio && fim ? `?inicio=${encodeURIComponent(inicio)}&fim=${encodeURIComponent(fim)}` : '';
  return fetchFromAPI<GeneralStats>(`/metrics-gerais${qs}`);
};

export const fetchLevelStats = (inicio?: string, fim?: string) => {
  const qs = inicio && fim ? `?inicio=${encodeURIComponent(inicio)}&fim=${encodeURIComponent(fim)}` : '';
  return fetchFromAPI<LevelStats>(`/status-niveis${qs}`);
};

export const fetchTechnicianRanking = (inicio?: string, fim?: string) => {
  const qs = inicio && fim ? `?inicio=${encodeURIComponent(inicio)}&fim=${encodeURIComponent(fim)}` : '';
  return fetchFromAPI<TechnicianRankingItem[]>(`/ranking-tecnicos${qs}`);
};

export const fetchNewTickets = () => {
  return fetchFromAPI<NewTicketItem[]>('/tickets-novos');
};
