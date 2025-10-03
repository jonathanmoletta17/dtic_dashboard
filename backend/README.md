# Backend – GLPI Dashboard API

Este backend fornece três endpoints para o dashboard, integrando com a API do GLPI.

## Endpoints
- `GET /api/v1/ranking-tecnicos` — ranking de técnicos por número de tickets (Top N).
- `GET /api/v1/metrics-gerais` — contagem geral por status (novos, em progresso, pendentes, resolvidos).
- `GET /api/v1/status-niveis` — contagem por nível (N1–N4) com agregados por status.

## Variáveis de Ambiente
Defina no arquivo `backend/.env` (carregado automaticamente pelo `backend/main.py`):
- `API_URL` — URL base da API GLPI (inclui `/apirest.php`).
- `APP_TOKEN` — token da aplicação GLPI.
- `USER_TOKEN` — token do usuário GLPI.
- `RANKING_TECHNICIAN_PARENT_GROUP_ID` — ID do grupo pai de técnicos (default `17`).

Exemplo:
```
API_URL=http://seu.glpi/apirest.php
APP_TOKEN=xxx
USER_TOKEN=yyy
RANKING_TECHNICIAN_PARENT_GROUP_ID=17
```

## Execução Local
- Requisitos: Python 3.10+, `pip install -r backend/requirements.txt`.
- Executar servidor:
```
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- Health check:
```
curl http://127.0.0.1:8000/
```

## Observações
- O cliente GLPI (`backend/glpi_client.py`) realiza autenticação e buscas paginadas.
- Evite armazenar segredos em código: use sempre `.env`.
- A busca de IDs de técnico em `ranking_logic.get_group_members` utiliza `forcedisplay[0]='2'` com fallback para `User.id`/`id`, compatível com variações do GLPI.

## Estrutura
- `api/` — routers dos endpoints.
- `logic/` — regras de negócio para ranking, métricas e tickets novos.
- `schemas.py` — modelos Pydantic para respostas.
- `glpi_client.py` — cliente GLPI com autenticação e helpers de busca.