# App DTIC

Este diretório representa o app DTIC no modelo de monorepo. A base do código já existe na raiz atual do projeto (frontend e backend).

Plano:
- Manter o código DTIC como está na raiz inicialmente.
- Após extrair Manutenção, podemos migrar DTIC para `apps/dtic/` para consolidar a estrutura.

Áreas DTIC principais (atuais):
- Backend: `backend/api/{ranking_router, stats_router, tickets_router}`, `backend/logic/{metrics_logic, ranking_logic, tickets_logic}`, `backend/schemas.py`.
- Frontend: rotas e telas DTIC em `frontend/src`.