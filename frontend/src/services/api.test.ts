import { describe, it, expect, vi, afterEach } from 'vitest';
import { fetchGeneralStats, fetchLevelStats, fetchTechnicianRanking, fetchNewTickets } from './api';

describe('API Services', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('fetchGeneralStats monta URL com range de datas e retorna dados', async () => {
    const mockData = { novos: 1, em_progresso: 2, pendentes: 3, resolvidos: 4 };
    const inicio = '2024-01-01';
    const fim = '2024-01-31';

    // Mock de fetch
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      statusText: 'OK',
      json: async () => mockData,
    });

    const data = await fetchGeneralStats(inicio, fim);
    expect(data).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith(
      `/api/v1/metrics-gerais?inicio=${encodeURIComponent(inicio)}&fim=${encodeURIComponent(fim)}`
    );
  });

  it('fetchLevelStats monta URL com range de datas e retorna dados', async () => {
    const mockData = {
      N1: { novos: 1, em_progresso: 2, pendentes: 3, resolvidos: 4, total: 10 },
      N2: { novos: 1, em_progresso: 2, pendentes: 3, resolvidos: 4, total: 10 },
      N3: { novos: 1, em_progresso: 2, pendentes: 3, resolvidos: 4, total: 10 },
      N4: { novos: 1, em_progresso: 2, pendentes: 3, resolvidos: 4, total: 10 },
    };
    const inicio = '2024-02-01';
    const fim = '2024-02-29';

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      statusText: 'OK',
      json: async () => mockData,
    });

    const data = await fetchLevelStats(inicio, fim);
    expect(data).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith(
      `/api/v1/status-niveis?inicio=${encodeURIComponent(inicio)}&fim=${encodeURIComponent(fim)}`
    );
  });

  it('fetchTechnicianRanking chama endpoint correto e retorna dados', async () => {
    const mockData = [
      { tecnico: 'Alice', tickets: 10, nivel: 'N2' },
      { tecnico: 'Bob', tickets: 8, nivel: 'N1' },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      statusText: 'OK',
      json: async () => mockData,
    });

    const data = await fetchTechnicianRanking();
    expect(data).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith('/api/v1/ranking-tecnicos');
  });

  it('fetchNewTickets chama endpoint correto e retorna dados', async () => {
    const mockData = [
      { id: 123, titulo: 'Falha no login', solicitante: 'Carlos', data: '2024-03-01' },
      { id: 122, titulo: 'Erro 500', solicitante: 'Ana', data: '2024-02-28' },
    ];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      statusText: 'OK',
      json: async () => mockData,
    });

    const data = await fetchNewTickets();
    expect(data).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith('/api/v1/tickets-novos');
  });

  it('lança erro detalhado quando resposta não é ok e retorna JSON com detail', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      statusText: 'Internal Server Error',
      json: async () => ({ detail: 'Erro interno ao buscar métricas gerais: X' }),
    });

    await expect(fetchGeneralStats()).rejects.toThrow('Erro interno ao buscar métricas gerais: X');
  });

  it('lança erro genérico quando resposta não é ok e JSON falha', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      statusText: 'Bad Request',
      json: async () => { throw new Error('invalid json'); },
    });

    await expect(fetchLevelStats()).rejects.toThrow('Erro de rede: Bad Request ao acessar o endpoint /status-niveis');
  });
});