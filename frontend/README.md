
# Frontend – Dashboard GLPI

Este frontend (Vite + React) consome a API do backend para exibir métricas do GLPI.

## Como funciona a integração com a API
- As chamadas à API são centralizadas em `src/services/api.ts` e usam `fetch`.
- O base path da API é `'/api/v1'`. Em desenvolvimento, o Vite faz proxy de `'/api'` para o backend.
- Proxy configurado em `vite.config.ts`:
  - `server.proxy['/api'] -> http://127.0.0.1:8000`

## Endpoints consumidos
- `GET /api/v1/metrics-gerais`
- `GET /api/v1/status-niveis`
- `GET /api/v1/ranking-tecnicos`
- `GET /api/v1/tickets-novos`

## Executar em desenvolvimento
1. Instale dependências:
   - `npm install`
2. Garanta que o backend esteja rodando em `http://127.0.0.1:8000`.
3. Inicie o frontend:
   - `npm run dev` (abre em `http://localhost:3000`)

## Observações
- Não é necessário configurar `VITE_API_BASE_URL`: o proxy já aponta `'/api'` para o backend.
- Se mudar a porta/host do backend, atualize `vite.config.ts` (seção `server.proxy`).
  