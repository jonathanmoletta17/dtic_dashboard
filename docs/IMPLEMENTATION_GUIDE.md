# Guia de Implementação: Conectando App_exemplo.tsx com a API GLPI

Este documento detalha os passos exatos para substituir os dados estáticos no arquivo `App_exemplo.tsx` pelos dados dinâmicos vindos da API, preservando 100% da estrutura visual do componente.

## 1. Análise da Fonte de Dados

A comunicação com o backend é feita através de funções pré-definidas no arquivo `@/services/api.ts`.

- **Funções a serem usadas:**
  - `fetchGeneralStats()`: Retorna estatísticas gerais.
  - `fetchLevelStats()`: Retorna estatísticas por nível (N1, N2, etc.).
  - `fetchTechnicianRanking()`: Retorna o ranking de técnicos.
  - `fetchNewTickets()`: Retorna uma lista de tickets novos.

- **Estrutura dos Dados (Tipos):** Os tipos de dados que a API retorna estão em `@/types/api.d.ts`.
  - `GeneralStats`: `{ novos: number, em_progresso: number, pendentes: number, resolvidos: number }`
  - `LevelStats`: `{ N1: LevelStatsDetail, N2: LevelStatsDetail, ... }`
    - `LevelStatsDetail`: `{ novos: number, em_progresso: number, pendentes: number, resolvidos: number, total: number }`
  - `TechnicianRankingItem`: `{ tecnico: string, tickets: number, nivel: string }`
  - `ApiNewTicketItem`: `{ id: number, titulo: string, solicitante: string, data: string }`
    - **Atenção:** Note que o frontend espera `requerente` e `data_abertura`, então faremos uma pequena conversão.

## 2. Lógica do Componente React

Dentro do componente `App` em `App_exemplo.tsx`, a seguinte lógica deve ser adicionada antes da declaração `return (...)`.

### 2.1. Importações

Adicione as seguintes importações no topo do arquivo:

```typescript
import { useState, useEffect } from 'react';
import { LoaderCircle, ServerCrash } from "lucide-react"; // Ícones para loading/erro
import { fetchGeneralStats, fetchLevelStats, fetchTechnicianRanking, fetchNewTickets } from '@/services/api';
import type { GeneralStats, LevelStats, TechnicianRankingItem, NewTicketItem as ApiNewTicketItem } from '@/types/api';

// Interface para os tickets como serão exibidos no frontend
interface DisplayTicketItem {
  id: number;
  titulo: string;
  requerente: string;
  data_abertura: string;
  description: string;
  status: string;
}

// Objeto de ticket vazio para preencher espaços se a API retornar menos de 8
const emptyTicket: DisplayTicketItem = { id: 0, titulo: '...', requerente: '...', data_abertura: '', description: '...', status: '...' };
```

### 2.2. Estados e Busca de Dados

Esta é a lógica que busca e armazena os dados da API.

```typescript
export default function App() {
  const [generalStats, setGeneralStats] = useState<GeneralStats | null>(null);
  const [levelStats, setLevelStats] = useState<LevelStats | null>(null);
  const [ranking, setRanking] = useState<TechnicianRankingItem[] | null>(null);
  const [newTickets, setNewTickets] = useState<DisplayTicketItem[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [time, setTime] = useState(new Date());

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [generalStatsData, levelStatsData, rankingData, apiTicketsData] = await Promise.all([
        fetchGeneralStats(),
        fetchLevelStats(),
        fetchTechnicianRanking(),
        fetchNewTickets(),
      ]);

      setGeneralStats(generalStatsData);
      setLevelStats(levelStatsData);
      setRanking(rankingData as TechnicianRankingItem[]);
      
      const displayTickets = (apiTicketsData as ApiNewTicketItem[]).map(item => ({
          id: item.id || 0,
          titulo: item.titulo,
          requerente: item.solicitante, // Mapeando solicitante -> requerente
          data_abertura: item.data,    // Mapeando data -> data_abertura
          status: 'Nova',
          description: `Chamado aberto por ${item.solicitante} para ${item.titulo}`
      }));
      setNewTickets(displayTickets);

      setTime(new Date());
    } catch (err: any) {
      console.error("Falha ao buscar dados do dashboard:", err);
      setError(err.message || 'Ocorreu um erro desconhecido.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleRefresh = () => {
    loadDashboardData();
  }

  // O return (...) do seu JSX vem aqui
```

## 3. Mapeamento e Substituição no JSX

Encontre e substitua os valores estáticos no seu JSX.

### 3.1. Header
- **Relógio**: Troque `17:38:57` por `{time.toLocaleTimeString('pt-BR')}`.
- **Botão de Refresh**: Adicione `onClick={handleRefresh}` e `disabled={isLoading}` ao botão com o ícone `RotateCcw`.

### 3.2. Corpo Principal (Wrapper de Loading/Erro)

Envolva todo o conteúdo principal (a `div` que contém as duas colunas) com a lógica de loading e erro.

```jsx
<main className="p-6 bg-gray-100 h-[calc(100vh-80px)] overflow-hidden">
  {isLoading ? (
    <div className="flex items-center justify-center h-full text-gray-500"><LoaderCircle className="w-8 h-8 animate-spin mr-4" /><span>Carregando dados...</span></div>
  ) : error ? (
    <div className="flex flex-col items-center justify-center h-full text-red-600"><ServerCrash className="w-12 h-12 mb-4" /><h2 className="text-xl font-semibold">Falha ao Carregar Dados</h2><p>{error}</p><Button onClick={handleRefresh} className="mt-6">Tentar Novamente</Button></div>
  ) : (
    <div className="flex gap-6 h-full">
      {/* ... Todo o seu conteúdo de colunas aqui ... */}
    </div>
  )}
</main>
```

### 3.3. Cards de Estatísticas Gerais

- **Novos**: `<p className="text-2xl ...">3</p>` -> `<p ...>{generalStats?.novos ?? 0}</p>`
- **Em Progresso**: `<p className="text-2xl ...">45</p>` -> `<p ...>{generalStats?.em_progresso ?? 0}</p>`
- **Pendentes**: `<p className="text-2xl ...">26</p>` -> `<p ...>{generalStats?.pendentes ?? 0}</p>`
- **Resolvidos**: `<p className="text-2xl ...">10.2K</p>` -> `<p ...>{generalStats?.resolvidos ?? 0}</p>`

### 3.4. Cards de Estatísticas de Nível (1-para-1)

- **Nível N1**:
  - Total: `1.495` -> `{levelStats?.N1?.total ?? 0}`
  - Novos: `1` -> `{levelStats?.N1?.novos ?? 0}`
  - Em Progr.: `8` -> `{levelStats?.N1?.em_progresso ?? 0}`
  - Pendentes: `3` -> `{levelStats?.N1?.pendentes ?? 0}`
  - Resolvidos: `1.483` -> `{levelStats?.N1?.resolvidos ?? 0}`
- **Nível N2**:
  - Total: `1.266` -> `{levelStats?.N2?.total ?? 0}`
  - ... e assim por diante para todos os campos de N2, N3 e N4.

### 3.5. Cards de Ranking de Técnicos (1-para-1)

- **#1**:
  - Nome: `Roberlâncio O.` -> `{ranking?.[0]?.tecnico.split(' ')[0] ?? 'N/A'}`
  - Nome Completo: `Arquitetos da Silva V.` -> `{ranking?.[0]?.tecnico ?? ''}`
  - Total/Resolvidos: `2.723` / `2.710` -> `{ranking?.[0]?.tickets ?? 0}`
- **#2**:
  - Nome: `Silvia M.` -> `{ranking?.[1]?.tecnico.split(' ')[0] ?? 'N/A'}`
  - ... e assim por diante para os rankings #2, #3 e #4.

### 3.6. Lista de Tickets Novos (1-para-1, SEM LOOP)

- **Contador de Tickets**: `8 tickets` -> `{newTickets?.length ?? 0} tickets`
- **Primeiro Ticket**:
  - ID: `#10387` -> `#{(newTickets?.[0] ?? emptyTicket).id}`
  - Status: `Nova` -> `{(newTickets?.[0] ?? emptyTicket).status}`
  - Título: `Acesso a Sistema...` -> `{(newTickets?.[0] ?? emptyTicket).titulo}`
  - Descrição: `Dados do formulário...` -> `{(newTickets?.[0] ?? emptyTicket).description}`
  - Requerente: `Angelo Diego da Rosa` -> `{(newTickets?.[0] ?? emptyTicket).requerente}`
  - Data: `11/09/2025` -> `{(newTickets?.[0]?.data_abertura) ? new Date(newTickets[0].data_abertura).toLocaleDateString('pt-BR') : '...'}`
- **Segundo Ticket**:
  - ID: `#10366` -> `#{(newTickets?.[1] ?? emptyTicket).id}`
  - ... e assim por diante para todos os 8 blocos de ticket, usando os índices `[1]`, `[2]`, ..., `[7]`.

