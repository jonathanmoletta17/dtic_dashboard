# Métricas Gerais e por Nível — Diferenças, Requisitos e Solução

Este documento consolida a análise das métricas gerais e por níveis, comparando a implementação atual com o projeto de referência, definindo requisitos para retornos corretos e propondo uma solução testada.

## 1. Diferenças Identificadas

- Filtro por Hierarquia e Status:
  - Referência: usa campos GLPI diretamente no `/search/Ticket` — Hierarquia (campo `8`) e Status (campo `12`).
  - Atual: contagem indireta via `Group_User` e técnicos atribuídos, sem uso consistente do campo `8` e com mapeamento de status incompleto.

- Mapeamento de Status GLPI:
  - Referência: `1=Novo, 2=Processando (atribuído), 3=Processando (planejado), 4=Pendente, 5=Solucionado, 6=Fechado`.
  - Atual: uso parcial; agregação inconsistente (por exemplo, considerar apenas `6` como resolvido).

- Métricas Gerais:
  - Referência: agrega `novos`, `em_progresso (2+3)`, `pendentes (4)`, `resolvidos (5+6)`.
  - Atual: inexistente ou incompleta.

## 2. Requisitos para Retornos Corretos

- Backend:
  - Consultas ao GLPI devem filtrar diretamente no endpoint `/search/Ticket`.
  - Critérios mínimos:
    - Hierarquia: `criteria[x][field]=8`, `searchtype=contains`, `value=<nível>` (ex.: `N1`).
    - Status: `criteria[y][field]=12`, `searchtype=equals`, `value=<statusId>`.
  - Agregação de status:
    - `novos`: `1`
    - `em_progresso`: `2 + 3`
    - `pendentes`: `4`
    - `resolvidos`: `5 + 6`
  - Eficiência: usar `range=0-0` e consumir `totalcount` para contagens.

- Frontend:
  - Consumir `/api/v1/metrics-gerais` (`GeneralStats`) e `/api/v1/status-niveis` (`LevelStats`).
  - Exibir métricas sem alteração de layout em produção (`App.tsx`).
  - Utilizar `App1.tsx` para testes de integração com os serviços:
    - `fetchGeneralStats()`
    - `fetchLevelStats()`

## 3. Proposta de Solução (Sem alterar produção)

- Scripts auxiliares de validação (GLPI direto):
  - `backend/debug_output/test_metrics_gerais.py`: valida agregação geral de status.
  - `backend/debug_output/test_metrics_por_nivel.py`: valida agregação por nível usando Hierarquia (campo `8`).

- Ajustes de backend (planejados, com base na validação):
  - Refatorar `metrics_logic.py` para filtrar por campos `8` e `12` diretamente na busca GLPI.
  - Implementar contadores usando `totalcount` e agregações descritas.
  - Garantir schemas coerentes (`GeneralStats`, `LevelStats`).

- Frontend de teste:
  - `App1.tsx`: integrar chamadas a `fetchGeneralStats` e `fetchLevelStats` e exibir resultados.

## 4. Plano de Teste e Validação

1) Validação direta no GLPI:
   - Executar os scripts auxiliares para obter contagens.
   - Confirmar consistência dos números ao variar níveis (`N1..N4`).

2) Validação do backend:
   - Chamar `GET /api/v1/metrics-gerais` e `GET /api/v1/status-niveis`.
   - Verificar `HTTP 200` e payloads conforme schemas.

3) Validação do frontend (App1):
   - Popular cards com números vindos dos serviços.
   - Conferir exibição sem erros e sem alterar `App.tsx` (produção).

## 5. Critérios de Aceite

- Scripts auxiliares retornam contagens coerentes com a base GLPI.
- Endpoints de backend respondem com `HTTP 200` e agregações corretas.
- `App1.tsx` exibe métricas corretas usando os serviços, sem alterar `App.tsx`.
- Documentação atualizada descrevendo campos, filtros, agregações e testes.