# Organização dos Projetos (Monorepo)

Este diretório `apps/` organiza os dois projetos enxutos em paralelo:

- `apps/dtic`: aplicação original do DTIC (frontend + backend existentes).
- `apps/manutencao`: aplicação separada para o dashboard de Manutenção (frontend + backend).

Há também a possibilidade de um módulo compartilhado (`packages/shared`) para utilitários comuns (cliente GLPI, cache, helpers), mantendo constantes e esquemas específicos em cada app para evitar mistura.

Estratégias suportadas:
- Monorepo: `apps/dtic`, `apps/manutencao`, e opcionalmente `packages/shared`.
- Dois repositórios separados: um para DTIC e outro para Manutenção; o compartilhado pode ser publicado como pacote ou submódulo.

Consulte os READMEs internos para o plano de extração e execução.