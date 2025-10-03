# Filtro Global de Data no Dashboard

Objetivo: permitir ao usuário selecionar um intervalo de datas único (global) que será aplicado de forma consistente em todas as métricas apresentadas no dashboard, sem alterar a lógica de negócio existente, mantendo simplicidade de uso, desempenho e manutenibilidade.

## Escopo
- Aplicar o mesmo intervalo de datas às métricas: gerais, por nível (N1–N4), ranking de técnicos, novos por período e quaisquer gráficos associados.
- Padronizar contratos de APIs e semântica de filtros de data.
- Não altera código agora; este documento especifica o que deverá ser criado e como integrar.

## Diretrizes de UX
- Componente global `DateRangePicker` posicionado no cabeçalho do dashboard.
- Padrões:
  - Intervalo inicial: últimos 30 dias, ou mês corrente (configurável).
  - Campo de data padrão: criação (`field 15`). O usuário pode alternar para modificação (`field 19`) via seletor simples (opcional).
- Interações:
  - Seleção deve validar `inicio <= fim`.
  - Inclusivo: `inicio` às 00:00:00 e `fim` às 23:59:59.
  - Estado persistido na URL (`?inicio=YYYY-MM-DD&fim=YYYY-MM-DD&campo_data=15`) para deep-link e compartilhamento.

## Contrato de API (Backend)
- Parâmetros de query padronizados em todos endpoints do dashboard:
  - `inicio` (string, `YYYY-MM-DD`, obrigatório)
  - `fim` (string, `YYYY-MM-DD`, obrigatório)
  - `campo_data` (int, opcional; default `15`=criação, `19`=modificação)

- Exemplos de endpoints (nomes ilustrativos com base em `backend/api/*.py`):
  - `GET /stats/general?inicio=2025-10-01&fim=2025-10-31&campo_data=15`
  - `GET /stats/levels?inicio=2025-10-01&fim=2025-10-31&campo_data=19`
  - `GET /ranking/technicians?inicio=2025-10-01&fim=2025-10-31&campo_data=15&top=10`
  - `GET /tickets/new?inicio=2025-10-01&fim=2025-10-31&campo_data=15`

- Respostas devem incluir metadados do intervalo aplicado:
```json
{
  "intervalo": {"inicio": "2025-10-01", "fim": "2025-10-31", "campo_data": 15},
  "data": { /* métrica específica */ }
}
```

## Semântica e Mapeamentos GLPI
- Campo de status: `field 12`.
- Campo de nível (hierarquia): `field 8` com valores `N1|N2|N3|N4` (contains).
- Campos de data:
  - Criação: `field 15`
  - Modificação: `field 19`

- Agregações de status (dashboard):
  - `novos`: `status_id=1`
  - `em_progresso`: `status_id=2` e `3`
  - `pendentes`: `status_id=4`
  - `resolvidos`: `status_id=5` e `6`

- Critério de data por intervalo (aplicado em todas as buscas `/search/Ticket`):
  - `morethan >= inicio` (campo `15` ou `19`)
  - `lessthan <= fim 23:59:59`

## Arquitetura de Backend (Proposta)
- `schemas.py`
  - Definir `DateRange` (pydantic): `inicio: date`, `fim: date`, `campo_data: int = 15`.
- `logic/utils/date_filters.py` (novo util):
  - `build_date_criteria(start: date, end: date, field_id: int) -> List[Criteria]` retorna critérios GLPI consistentes.
  - Responsável por normalizar `fim` para `23:59:59`, validar intervalo e converter datas.
- Integração nas lógicas:
  - `metrics_logic.py`: aplicar `build_date_criteria` aos cálculos das métricas gerais.
  - `ranking_logic.py`: incluir os critérios de data nas buscas de contagem por técnico.
  - `tickets_logic.py`: aplicar o mesmo critério a “novos por período”.
- `api/*_router.py`:
  - Parsear `DateRange` em todos handlers do dashboard.
  - Propagar `DateRange` às funções de lógica.

## Arquitetura de Frontend (Proposta)
- Componente: `src/components/DateRangePicker.tsx`
  - Props: `value`, `onChange`, `fieldOption` (criação/modificação).
  - Validação client-side simples e mensagens amigáveis.
- Estado Global: `src/services/dateFilterContext.ts`
  - `DateFilterProvider` com estado `{ inicio, fim, campo_data }`.
  - Hook `useDateFilter()` para leitura/atualização do estado.
  - Sincronização com URL (query params) na montagem e a cada alteração.
- Serviços: `src/services/api.ts`
  - Funções que leem o estado do filtro global e anexam `inicio`, `fim`, `campo_data` a todas requisições do dashboard.
  - Requisições existentes mantidas; apenas adicionam os params.

## Fluxo End-to-End
1. Usuário seleciona intervalo no `DateRangePicker`.
2. Contexto global atualiza `{inicio, fim, campo_data}` e sincroniza na URL.
3. Páginas do dashboard disparam refetch das métricas.
4. Backend recebe params e aplica `build_date_criteria` em todas as consultas GLPI.
5. Respostas retornam dados + metadados do intervalo, garantindo consistência visual.

## Boas Práticas
- Consistência: uma única função util para critérios de data no backend.
- Observabilidade: logar intervalo aplicado e tempo de resposta por endpoint.
- Resiliência: defaults seguros se params ausentes; mensagens claras em erro de validação.
- Desempenho:
  - Ranking: consultas em paralelo por técnico com `range=0-0` (apenas `totalcount`).
  - Cache: chavear por `inicio|fim|campo_data|endpoint` com TTL curto.
  - Evitar over-fetch, limitar `top` em ranking.
- Segurança: validar formato de datas, evitar injeção em critérios.
- Timezone: fixar timezone (servidor) e documentar.

## Testes
- Unidades (backend):
  - `build_date_criteria`: datas válidas/invalidas; inclusividade; conversão para `fim 23:59:59`.
  - Agregações de status: somas e mapeamentos.
- Integração:
  - Cada endpoint com o mesmo intervalo retorna dados consitentes e soma geral bate.
  - Ranking retorna os mesmos técnicos do dashboard atual para o intervalo.
- E2E:
  - Simular seleção no `DateRangePicker` e verificar a atualização de todos cards/gráficos.
- Comparativo (já disponível): scripts de teste diretos ao GLPI (`backend/debug_output/*_por_data.py`).

## Critérios de Aceite
- Todas as métricas do dashboard respeitam o mesmo intervalo (e campo de data) selecionado.
- Metadados do intervalo retornam em todas respostas.
- Diferenças entre endpoints se reduzem ao mínimo esperado pelo escopo da métrica.
- Performance aceitável nos intervalos típicos (e.g., 30–90 dias).

## Riscos e Mitigações
- Divergência de semântica entre métricas: mitigar com util único de critérios.
- Volume de consultas (ranking com muitos técnicos): limitar `top`, cache e paralelismo controlado.
- Timezone: padronizar e comunicar.

## Exemplos
Requests:
```
GET /stats/general?inicio=2025-10-01&fim=2025-10-31&campo_data=15
GET /stats/levels?inicio=2025-10-01&fim=2025-10-31&campo_data=19
GET /ranking/technicians?inicio=2025-10-01&fim=2025-10-31&campo_data=15&top=10
```

Response (general):
```json
{
  "intervalo": {"inicio": "2025-10-01", "fim": "2025-10-31", "campo_data": 15},
  "data": {
    "novos": 3,
    "em_progresso": 7,
    "pendentes": 2,
    "resolvidos": 12,
    "total": 24
  }
}
```

## Implementação (Passos)
1. Frontend
  - Criar `DateRangePicker.tsx` e `dateFilterContext.ts`.
  - Integrar o picker ao layout do dashboard e sincronizar com a URL.
  - Atualizar serviços para anexar params do filtro global.
2. Backend
  - Adicionar `DateRange` em `schemas.py`.
  - Criar `logic/utils/date_filters.py` com `build_date_criteria`.
  - Atualizar handlers em `api/*_router.py` para aceitar os params e propagar à lógica.
  - Injetar critérios de data em `metrics_logic.py`, `ranking_logic.py`, `tickets_logic.py`.
3. Testes e validação
  - Implementar testes unitários e integração.
  - Validar com scripts diretos GLPI (`test_metrics_gerais_por_data.py`, `test_status_niveis_por_data.py`, `test_ranking_tecnicos_por_data.py`).
4. Observabilidade e performance
  - Instrumentar logs e, se aplicável, métricas de tempo de resposta.
  - Introduzir cache por intervalo.

## Rollout
- Feature flag para habilitar o filtro global de data.
- Lançamento gradual, monitoramento e fallback para intervalo padrão.

---
Este documento é a referência de implementação para tornar o filtro global de datas simples, objetivo e consistente em todo o dashboard, seguindo boas práticas de programação e manutenção.