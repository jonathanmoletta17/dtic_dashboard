# DTIC Dashboard

Este repositório contém o backend (FastAPI) e o frontend (Vite) do dashboard de métricas do GLPI.

## Visão Geral
- Backend: `backend/` — API FastAPI com endpoints de métricas e ranking.
- Frontend: `frontend/` — aplicação Vite/TS que consome a API.
- Documentação: `docs/` — notas técnicas, auditorias e guias.

## Como executar o Backend
1. Configure as variáveis de ambiente (veja `backend/README.md` para detalhes):
   - `API_URL`, `APP_TOKEN`, `USER_TOKEN`
   - `RANKING_TECHNICIAN_PARENT_GROUP_ID` (opcional)
2. Instale dependências do backend:
   - `python -m pip install -r backend/requirements.txt`
3. Execute o servidor de desenvolvimento:
   - `python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000`

Documentação completa do backend: consulte `backend/README.md`.

## Como executar o Frontend
1. Instale dependências:
   - `cd frontend`
   - `npm install`
2. Execute o servidor de desenvolvimento:
   - `npm run dev`

## Notas
- O diretório `backend/middleware/` está vazio e será removido em breve para manter o repositório limpo.
- As auditorias e plano de limpeza estão descritos em `docs/revisao_codigo_dashboard_glpi.md`.