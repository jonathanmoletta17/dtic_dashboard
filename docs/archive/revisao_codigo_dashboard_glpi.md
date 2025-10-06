# Revisão de Código – Dashboard GLPI

Este documento consolida a revisão do backend do dashboard GLPI, mapeando código ativo, identificando partes não utilizadas ou sensíveis, validando os endpoints principais e propondo um plano de limpeza antes do push para o GitHub.

## Objetivo
- Garantir que o repositório contenha apenas o código necessário ao dashboard e às métricas do GLPI.
- Remover trechos demonstrativos/sensíveis, evitar dependências não usadas e reduzir risco operacional.

## Escopo Atual do Backend
- `backend/main.py`: ponto de entrada FastAPI; carrega `.env` do backend e inclui três routers.
- Routers (ativos):
  - `backend/api/ranking_router.py` → usa `generate_technician_ranking`.
  - `backend/api/stats_router.py` → usa `generate_level_stats`, `generate_general_stats`.
  - `backend/api/tickets_router.py` → usa `get_new_tickets`.
- Lógica (ativa):
  - `backend/logic/ranking_logic.py`: `get_group_members`, `generate_technician_ranking`, `count_tickets_by_tech_parallel`.
  - `backend/logic/metrics_logic.py`: `generate_level_stats`, `generate_general_stats`.
  - `backend/logic/tickets_logic.py`: `get_new_tickets`.
- Cliente GLPI: `backend/glpi_client.py`.
  - Funções usadas: `authenticate`, `search_paginated`, `get_user_names_in_batch_with_fallback`.
  - Funções não usadas atualmente: `list_search_options`, `search_count`, `get_tickets`.
  - Bloco `if __name__ == "__main__"`: contém tokens sensíveis de teste e chamadas de demonstração.
- Outros:
  - `backend/middleware/`: diretório vazio (sem arquivos).
  - `diagnose_ranking.py`: script de diagnóstico (dev-only), sem segredos hardcoded; lê `.env` do backend.
  - `tests/*`: scripts e experimentos de validação; não expõem segredos.

## Mapeamento de Uso por Função
- `glpi_client.authenticate` → usado por todos os routers.
- `glpi_client.search_paginated` → usado em `tickets_logic.get_new_tickets` e em testes.
- `glpi_client.get_user_names_in_batch_with_fallback` → usado em `tickets_logic.get_new_tickets` e `ranking_logic.generate_technician_ranking`.
- `glpi_client.list_search_options`, `search_count`, `get_tickets` → não referenciados por endpoints ou lógica ativa do dashboard.
- `ranking_logic.get_user_name` → não referenciado na lógica atual (uso substituído pelo batch resolver do `glpi_client`).

## Validações Executadas
- Servidor iniciado localmente (`python -m uvicorn backend.main:app --reload`).
- Respostas coletadas:
  - `GET /api/v1/metrics-gerais` → `{ "novos": 4, "em_progresso": 57, "pendentes": 38, "resolvidos": 10348 }`.
  - `GET /api/v1/status-niveis` → dados por nível N1..N4 com totais coerentes (amostra: N2 total 2611, N3 total 5563).
  - `GET /api/v1/ranking-tecnicos` → validado anteriormente; retorna lista ordenada com técnicos e contagens.

## Itens Sensíveis/Redundantes Identificados
- `backend/glpi_client.py::__main__`:
  - Contém `API_URL`, `APP_TOKEN`, `USER_TOKEN` hardcoded. Deve ser removido antes do push público para eliminar segredo e uso indevido em produção.
- Funções não usadas (manter ou remover):
  - `glpi_client.list_search_options`, `glpi_client.search_count`, `glpi_client.get_tickets`.
  - `ranking_logic.get_user_name`.
- Diretório vazio: `backend/middleware/`.

## Recomendações de Limpeza (Plano)
1. Remover bloco `__main__` de `backend/glpi_client.py` (tokens hardcoded e chamadas de demo).
2. Remover funções não utilizadas:
   - `glpi_client.list_search_options`, `search_count`, `get_tickets`.
   - `ranking_logic.get_user_name` (uso substituído por batch resolver).
3. Excluir diretório vazio `backend/middleware/`.
4. Documentar variáveis de ambiente suportadas em `backend/README.md` (API_URL, APP_TOKEN, USER_TOKEN, RANKING_TECHNICIAN_PARENT_GROUP_ID).
5. Logging mínimo nos endpoints (já existe um print de erro); manter leve para produção.
6. Opcional (organização): mover scripts de testes/experimentos para `scripts/` ou manter em `tests/` com README explicativo.

## Observações Técnicas
- Correções aplicadas previamente:
  - Extração de IDs em `get_group_members` alinhada ao GLPI (`forcedisplay[0]='2'` e fallback para `User.id`/`id`).
  - Ranking computado via `totalcount` por técnico (campo `5`), reduzindo custo de paginação.
  - Métricas gerais/por nível consultam diretamente `/search/Ticket` por status/hierarquia.
- Os endpoints estão respondendo com dados consistentes; não há erros aparentes na camada de roteadores.

## Próximos Passos
- Aprovar o plano de limpeza e aplicar as remoções listadas.
- Rodar novamente a validação dos três endpoints principais pós-limpeza.
- Revisar README e documentação para garantir onboarding e deploy limpos.

—
Responsável: Equipe de Desenvolvimento
Data: Atual
Status: Revisão concluída; aguardando aprovação para limpeza