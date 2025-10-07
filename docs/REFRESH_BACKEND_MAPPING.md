# Backend DTIC – Mapeamento do Mecanismo de Atualização (Refresh)

Este documento descreve, em profundidade, como o backend da aplicação DTIC lida com atualização de dados quando o frontend realiza polling periódico (por exemplo, 12–15 segundos). Ele mapeia variáveis `.env`, pontos de uso no código, políticas de cache, sessão e implicações práticas para alinhamento com o refresh do frontend. Não há agendadores no backend; toda atualização ocorre sob demanda, quando o frontend chama os endpoints.

## Visão Geral
- O frontend executa polling configurável via `.env` para consultar o backend em intervalo fixo.
- O backend não agenda atualizações; ele responde às chamadas com dados da API GLPI.
- Para reduzir latência e carga externa, o backend utiliza cache em memória com TTL curto.
- A autenticação com GLPI também é cacheada (session-token) com TTL curto.

## Variáveis de Ambiente no Backend
Arquivo de referência: `apps/dtic/backend/.env.example`

- `API_URL` (obrigatório)
  - URL base da API GLPI, incluindo `apirest.php`.
  - Usada em todos os roteadores ao autenticar e consultar o GLPI.

- `APP_TOKEN` (obrigatório)
  - Token de aplicação do GLPI.
  - Usado na autenticação e em chamadas subsequentes.

- `USER_TOKEN` (obrigatório)
  - Token de usuário do GLPI.
  - Usado na autenticação e em chamadas subsequentes.

- `CACHE_TTL_SEC` (opcional, padrão `300`)
  - TTL (segundos) para respostas memorizadas no cache interno do backend.
  - Afeta diretamente a “frescura” dos dados retornados durante o polling do frontend.

- `SESSION_TTL_SEC` (opcional, padrão `300`)
  - TTL (segundos) para reuso do `Session-Token` do GLPI.
  - Reduz chamadas a `initSession` e troca de entidade; melhora performance e estabilidade.

- `RANKING_TECHNICIAN_PARENT_GROUP_ID` (opcional, padrão `17`)
  - ID do grupo pai de técnicos usado para computar ranking.
  - Impacta quem entra no ranking, não o mecanismo de refresh em si.

## Onde e Como São Carregadas
- `main.py` carrega variáveis via `dotenv` do arquivo `.env` localizado em `apps/dtic/backend/`.
- Os roteadores (`ranking_router.py`, `stats_router.py`, `tickets_router.py`) leem as variáveis dentro das funções de endpoint, garantindo que `.env` já esteja carregado.

## Políticas de Cache e Sessão

### Cache de Respostas (Dados)
- Módulo: `backend/utils/cache.py`
- Implementação: `SimpleCache` com TTL padrão de `CACHE_TTL_SEC`.
- Uso nos endpoints:
  - `stats_router.py`
    - Endpoints: `/status-niveis` e `/metrics-gerais`.
    - Guardam o resultado em cache com chave que inclui filtro de datas (quando presente) e conjunto de status.
  - `ranking_router.py`
    - Endpoint: `/ranking-tecnicos`.
    - Cacheia o Top N com chave incluindo intervalo e limite.
- Efeito sobre refresh: enquanto a entrada de cache for válida, o backend retornará o mesmo payload mesmo que o frontend consulte a cada 12–15 segundos.

### Cache de Sessão (Autenticação GLPI)
- Módulo: `backend/glpi_client.py`
- Variável: `SESSION_TTL_SEC`.
- Comportamento: autenticação (`initSession`) é reaproveitada por `SESSION_TTL_SEC` segundos; após expirar, o backend reautentica na próxima chamada.

## Timeouts e Robustez
- Chamadas GLPI usam timeouts curtos (tipicamente `(2–3s, 4–6s)` conectado/leitura).
- Exceções específicas são levantadas e mapeadas em HTTP 4xx/5xx no nível do router (ex.: `GLPIAuthError`, `GLPINetworkError`, `GLPISearchError`).
- Logging central: `backend/utils/logging_setup.py` define formato e nível INFO.

## Interação com o Polling do Frontend
- DTIC Frontend:
  - `.env.production` inclui `VITE_REALTIME_POLL_INTERVAL_SEC` (valor em milissegundos; ex.: `15000`).
  - Em `src/App.tsx`, o valor é lido e usado diretamente como intervalo (ms).
- Manutenção Frontend:
  - Em `src/MaintenanceDashboard.tsx`, o intervalo é lido de `VITE_REALTIME_POLL_INTERVAL_MS` ou `VITE_REALTIME_POLL_INTERVAL_SEC` (quando definido em segundos) e convertido para ms.
- Alinhamento recomendado:
  - Ajuste `CACHE_TTL_SEC` no backend para equilibrar frescor e carga na API GLPI.
  - Ajuste o intervalo do frontend conforme necessidade de atualização visual.
  - Se o intervalo do frontend for inferior ao `CACHE_TTL_SEC`, o usuário verá dados estáveis até a expiração do cache.

## Chaves de Cache e Filtros de Datas
- `status-niveis`: chave inclui `inicio`/`fim` (quando presentes).
- `metrics-gerais`: chave inclui o conjunto fixo de status (NEW, ASSIGNED, PLANNED, IN_PROGRESS, SOLVED, CLOSED) e `inicio`/`fim`.
- `ranking-tecnicos`: chave inclui `inicio`/`fim` e `limit` (Top N).
- Implicação: mudando o filtro de datas, a chave muda e força recomputação (cache miss) mesmo que TTL ainda esteja válido.

## Checklist de Configuração (DTIC)
- Preencher `.env` do backend com `API_URL`, `APP_TOKEN`, `USER_TOKEN` válidos.
- Definir `CACHE_TTL_SEC` conforme SLA de frescor (ex.: `120` para 2 minutos).
- Definir `SESSION_TTL_SEC` conforme estabilidade desejada (ex.: `600`).
- No frontend, ajustar `VITE_REALTIME_POLL_INTERVAL_*` para o intervalo de polling (ex.: `12000` ms para ~12 segundos).

## Diretrizes para Reprodução no Dashboard de Manutenção
- Backend de Manutenção deve expor endpoints equivalentes e usar cache com TTL apropriado.
- Frontend de Manutenção já suporta `VITE_REALTIME_POLL_INTERVAL_MS` e `VITE_REALTIME_POLL_INTERVAL_SEC`.
- Garanta que `VITE_API_BASE_URL` aponte para `/api/v1` do backend correto.
- Alinhe `CACHE_TTL_SEC` com o uso esperado: se o objetivo é refletir mudanças com menos latência, reduza o TTL.

## Referências de Código
- Carregamento `.env`: `apps/dtic/backend/main.py`.
- Cache: `apps/dtic/backend/utils/cache.py`.
- Sessão GLPI: `apps/dtic/backend/glpi_client.py`.
- Endpoints e cache:
  - `apps/dtic/backend/api/stats_router.py` – `/status-niveis`, `/metrics-gerais`.
  - `apps/dtic/backend/api/ranking_router.py` – `/ranking-tecnicos`.
  - `apps/dtic/backend/api/tickets_router.py` – `/tickets-novos`.