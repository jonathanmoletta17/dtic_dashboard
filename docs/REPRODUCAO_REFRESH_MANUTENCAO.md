# Reprodução do Refresh no Dashboard de Manutenção (Base de Conhecimento)

Este guia descreve como reproduzir o comportamento de refresh periódico do dashboard DTIC no dashboard de Manutenção, usando os mesmos princípios de backend (TTL de cache e sessão) e configurações de frontend (polling via `.env`). Não há alterações de código — apenas configuração e entendimento operacional.

## 1) Backend: Princípios e Ajustes
- Não há agendador no backend. O refresh vem das chamadas do frontend.
- Use cache com TTL curto para balancear frescor x carga:
  - `CACHE_TTL_SEC`: segundos de validade das respostas cacheadas.
  - `SESSION_TTL_SEC`: segundos de reuso do Session-Token do GLPI.
- Recomendações práticas:
  - Se o frontend atualizar a cada ~12–15s, considere `CACHE_TTL_SEC` entre 60–180s para suavizar picos e manter dados relativamente atualizados.
  - Aumente `SESSION_TTL_SEC` (ex.: 600) para reduzir autenticação em picos de tráfego.

## 2) Frontend de Manutenção: Configuração de Polling
- O arquivo `src/MaintenanceDashboard.tsx` suporta:
  - `VITE_REALTIME_POLL_INTERVAL_MS`: intervalo de polling em milissegundos.
  - `VITE_REALTIME_POLL_INTERVAL_SEC`: intervalo em segundos (convertido para ms).
- Defina uma destas variáveis no `.env` de produção/dev do frontend de Manutenção:
  - Exemplo para ~12s:
    - `VITE_REALTIME_POLL_INTERVAL_MS=12000`
    - ou `VITE_REALTIME_POLL_INTERVAL_SEC=12`
- Defina também `VITE_API_BASE_URL` apontando ao backend de Manutenção (ou proxy do Vite):
  - Em dev: normalmente `/api/v1` com proxy.
  - Em produção: URL absoluto, ex.: `http://127.0.0.1:8010/api/v1`.

## 3) Como os Parâmetros Afetam o Comportamento
- Polling do frontend consulta endpoints de dados periodicamente.
- O backend responde com dados possivelmente cacheados por `CACHE_TTL_SEC`.
- Se o intervalo de polling for menor que `CACHE_TTL_SEC`, o usuário verá dados estáveis até expirar o cache.
- Mudança de filtros (ex.: `inicio`/`fim`) altera a chave de cache, forçando recomputação.

## 4) Passo a Passo de Reprodução
- Backend de Manutenção:
  - Crie `.env` com `API_URL`, `APP_TOKEN`, `USER_TOKEN` válidos.
  - Ajuste `CACHE_TTL_SEC` e `SESSION_TTL_SEC` conforme necessidades.
- Frontend de Manutenção:
  - Crie/edite `.env.production` (ou `.env.local`) com:
    - `VITE_API_BASE_URL=/api/v1` (dev com proxy) ou URL absoluta.
    - `VITE_REALTIME_POLL_INTERVAL_MS=12000` (ou `VITE_REALTIME_POLL_INTERVAL_SEC=12`).
- Verifique no navegador:
  - A cada ~12s, os cartões e rankings atualizam.
  - Logs do backend devem mostrar `cache_hit=true/false` conforme expiração e filtros.

## 5) Dicas de Observabilidade
- Logging do backend (`INFO`) mostra hits/misses de cache, TTL aplicado e erros de rede/autenticação.
- Ajuste TTLs se o comportamento percebido for “lento para atualizar” ou “pressiona demais o GLPI”.

## 6) Referências
- Backend DTIC: `apps/dtic/backend`.
- Frontend Manutenção: `apps/manutencao/frontend`.
- Mapeamento detalhado: `docs/REFRESH_BACKEND_MAPPING.md`.