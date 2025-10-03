# Plano de Testes — Filtros de Data para Métricas do Dashboard

Este documento orienta, passo a passo, como validar filtros de data para todas as métricas do dashboard (gerais, por nível, ranking de técnicos e tickets novos) usando consultas diretas à API GLPI, sem alterar o backend de produção. Foi escrito para que outra IA/engenheiro possa seguir e executar os testes de forma reprodutível.

## Objetivo
- Verificar corretamente os números retornados ao aplicar intervalos de data nas métricas.
- Definir critérios de consulta consistentes (campos, `searchtype`, agregações) e aceitar variações do GLPI.
- Produzir saídas JSON e evidências que permitam comparar com os endpoints do backend.

## Pré-requisitos
- `backend/.env` configurado com `API_URL`, `APP_TOKEN`, `USER_TOKEN`.
- Acesso à API GLPI funcional; o backend pode ou não estar rodando (para comparação com endpoints).
- Python 3.10+ e `requests` instalado (já previsto no `backend/requirements.txt`).

## Mapeamento de Campos GLPI (Tickets)
- `12` — Status do ticket.
- `8` — Hierarquia/Nível (strings contendo “N1”, “N2”, …). [Usado em métricas por nível]
- `5` — `users_id_tech` (técnico atribuído). [Usado em ranking de técnicos]
- `15` — Data de criação do ticket (creation/opening date). [Default para filtro de data]
- `19` — Data de modificação/atualização (last update). [Opcional]
- Observação: Algumas instâncias GLPI usam campo distinto para “data de fechamento” (ex.: `closedate`). Se o objetivo for “tickets resolvidos no intervalo”, validar qual é o campo correto na sua instância e ajustar.

## Convenções de Filtro de Data
- `searchtype` recomendados:
  - `morethan` para limite inferior (>= início)
  - `lessthan` para limite superior (<= fim)
- Formato de data:
  - `YYYY-MM-DD` ou `YYYY-MM-DD HH:MM:SS`. Se o usuário informar apenas `YYYY-MM-DD` para `fim`, incluir `23:59:59` para fechar o dia.
- `range=0-0` e `uid_cols=1` para obter `totalcount` de maneira rápida.

## Agregação de Status (Métrica do Dashboard)
- `novos`: `1`
- `em_progresso`: `2 + 3`
- `pendentes`: `4`
- `resolvidos`: `5 + 6`

## Estrutura dos Critérios (`/search/Ticket`)
- Geral por data e status:
  - `criteria[0]`: `{ field: <campo_data>, searchtype: morethan, value: <inicio> }`
  - `criteria[1]`: `{ link: AND, field: <campo_data>, searchtype: lessthan, value: <fim> }`
  - `criteria[2]`: `{ link: AND, field: 12, searchtype: equals, value: <status_id> }`
- Por nível (adicionar filtro de hierarquia):
  - `criteria[x]`: `{ link: AND, field: 8, searchtype: contains, value: N1|N2|N3|N4 }`
- Por técnico (ranking):
  - `criteria[x]`: `{ link: AND, field: 5, searchtype: equals, value: <user_id_tech> }`

## Scripts de Validação

### 1) Métricas Gerais por Intervalo de Data
- Arquivo: `backend/debug_output/test_metrics_gerais_por_data.py` (já criado).
- Uso:
  - `python backend/debug_output/test_metrics_gerais_por_data.py --inicio 2025-10-01 --fim 2025-10-31`
  - `python backend/debug_output/test_metrics_gerais_por_data.py --inicio 2025-10-01 --fim 2025-10-31 --campo-data 19`
- Saída:
  - JSON em `backend/debug_output/output/metrics_gerais_por_data.json` com campos: `novos`, `em_progresso`, `pendentes`, `resolvidos`, `total`, além do intervalo usado.
- Critério de sucesso:
  - Os números devem ser consistentes com chamadas diretas ao GLPI e, idealmente, com `/api/v1/metrics-gerais` quando comparado em mesma janela temporal (nota: o endpoint atual não aceita filtro de data; comparação serve para sanity check).

### 2) Métricas por Nível (N1–N4) com Intervalo de Data
- Proposta de script: `backend/debug_output/test_status_niveis_por_data.py`.
- Lógica:
  - Para cada nível em `N1..N4` e cada `status_id` em `1..6`, aplicar os critérios de data + hierarquia + status, somando nos agregados `novos`, `em_progresso`, `pendentes`, `resolvidos` e total.
- Pseudocódigo:
  - `count_level_status(headers, api_url, nivel, status_id, inicio, fim, campo_data)` → retorna `totalcount`.
  - Estrutura de resultado:
    - `{ "N1": { "novos": n, "em_progresso": x, "pendentes": y, "resolvidos": z, "total": t }, ... }`
- Critério de sucesso:
  - Soma dos níveis deve ser coerente com a métrica geral por data em mesma janela (variações podem ocorrer se “Sem Grupo/Outro Grupo” forem considerados; documentar se necessário).

### 3) Ranking de Técnicos com Intervalo de Data
- Proposta de script: `backend/debug_output/test_ranking_tecnicos_por_data.py`.
- Lógica:
  - Recuperar técnicos ativos sob o grupo pai (mesma abordagem de `ranking_logic`).
  - Para cada técnico, contar tickets com critérios de data + técnico (`field=5`), opcionalmente com filtros por status para breakdown.
- Critérios:
  - Total por técnico: `{ data_range } + { field: 5, equals: user_id_tech }`.
  - Breakdown por status: somar conforme agregação de status.
- Critério de sucesso:
  - Ordenação por total e amostra top N consistente com GLPI.

### 4) Tickets Novos por Intervalo de Data
- Proposta de script: `backend/debug_output/test_tickets_novos_por_data.py`.
- Lógica:
  - Filtro por `status_id=1` (novos) + intervalo de data.
  - (Opcional) Por nível: adicionar `field=8` `contains` para N1..N4.
- Critério de sucesso:
  - Consistência com números do GLPI e validação cruzada com métricas gerais (parte “novos”).

## Formato de Saída e Persistência
- Cada script deve persistir JSON em `backend/debug_output/output/` com nome descritivo.
- Incluir no JSON os parâmetros usados (intervalo, campo de data, filtros adicionais) para rastreabilidade.

## Comparação com Endpoints do Backend
- Endpoints relevantes:
  - `GET /api/v1/metrics-gerais`
  - `GET /api/v1/status-niveis`
  - `GET /api/v1/ranking-tecnicos`
  - `GET /api/v1/tickets-novos`
- Observação: Os endpoints atuais não aceitam filtros de data. A comparação serve como validação qualitativa na mesma janela temporal (quando fizer sentido) e para detectar discrepâncias.

## Troubleshooting
- `ECONNREFUSED` no proxy frontend: garantir que backend está estável; evitar `--reload` durante testes de carga; confirmar `vite.config.ts` proxy para `http://127.0.0.1:8000`.
- `searchtype` não funciona: algumas instâncias GLPI usam variações; testar `greaterthan/lessthan` se `morethan/lessthan` falharem.
- IDs de campos variam: priorizar nomes de campos em `forcedisplay` quando necessário e validar retorno; documentar diferenças.
- Timezone: assegurar que o intervalo considera a zona correta; incluir `23:59:59` no fim do dia quando necessário.
- Rate limit/desempenho: usar `range=0-0` e `totalcount`; evitar consultas desnecessárias; serializar chamadas se necessário.

## Critérios de Aceite
- Scripts executam sem erro, autenticam no GLPI e retornam JSON com contagens > 0 em janelas realistas.
- Contagens são estáveis ao repetir execução com o mesmo intervalo (salvo alterações no GLPI).
- Métricas por nível somam de forma coerente com métricas gerais em janelas estáveis (documentar diferenças esperadas se existirem).
- Ranking por data reflete ordem esperada com base em registros GLPI.

## Próximos Passos (Opcional)
- Adicionar parâmetro de data nos endpoints do backend e manter agregação idêntica aos scripts.
- Adicionar testes automatizados (pytest) com mocks da API GLPI para garantir estabilidade.
- Criar dashboard interno de validação que lê os JSONs gerados e exibe discrepâncias.

## Referências
- `backend/debug_output/test_metrics_gerais_por_data.py`
- `backend/logic/metrics_logic.py` (agregação por status)
- `docs/METRICS_TECHNICAL_SOLUTION.md`
- `docs/revisao_metricas_gerais_and_niveis.md`
- `docs/metricas_niveis_analise_copilot.md`