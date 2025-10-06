# Guia de Uso — Auditoria de Discrepância de Níveis

Este documento descreve o uso e o funcionamento do script de auditoria que valida, de forma automática, as discrepâncias entre as métricas gerais e as métricas por níveis (N1–N4) no GLPI.

## Visão Geral
- Script principal: `backend/debug_output/breakdown_sem_grupo.py`
- Objetivo: comparar o total geral de tickets com a soma dos tickets classificados estritamente em N1–N4, identificando com clareza quanto da diferença é composta por:
  - `SemGrupo`: tickets com campo 8 vazio/ausente.
  - `OutroGrupo`: tickets cujo campo 8 não contém apenas N1–N4 (ex.: valores compostos ou grupo raiz sem sufixo de nível).
- Saída: JSON completo para depuração + Relatório tabular legível com colunas de verificação.

## Pré‑requisitos
- Python 3.10+.
- Variáveis de ambiente configuradas em `backend/.env`:
  - `API_URL`: URL base da API GLPI.
  - `APP_TOKEN`: token de aplicação.
  - `USER_TOKEN`: token de usuário.

Exemplo de `backend/.env`:
```
API_URL=https://seu-glpi/api
APP_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
USER_TOKEN=yyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

## Como Executar
1. No diretório raiz do projeto:
   - Windows: `python backend\debug_output\breakdown_sem_grupo.py`
   - Linux/macOS: `python backend/debug_output/breakdown_sem_grupo.py`
2. O script realiza autenticação, busca paginada por status e produz a saída em dois formatos:
   - JSON estruturado (primeiro bloco impresso).
   - Relatório tabular legível (segundo bloco), com totais e notas.

## Mapeamento de Status
O script consolida os status GLPI nos grupos usados no dashboard:
- `novos`: status 1.
- `em_progresso`: status 2 e 3.
- `pendentes`: status 4.
- `resolvidos`: status 5 e 6.

## Colunas do Relatório
- `Geral`: total de tickets do grupo de status.
- `N1–N4`: total de tickets cujo campo 8 contém estritamente N1/N2/N3/N4.
- `SemGrupo`: total de tickets com campo 8 vazio/ausente.
- `OutroGrupo`: total de tickets com campo 8 diferente de N1–N4 (ex.: valores compostos).
- `Dif`: `Geral − N1–N4`.
- `SomaOK?`: verifica se `Geral = N1–N4 + SemGrupo + OutroGrupo`.
- `Dif = SemGrupo?`: verifica se `Dif == SemGrupo`.
- `Dif = Sem+Outro?`: verifica se `Dif == SemGrupo + OutroGrupo`.

## Interpretação Rápida
- Se `SomaOK?` for True em todas as linhas (incluindo TOTAL), os números estão consistentes.
- Se `Dif = Sem+Outro?` for True, toda a diferença entre `Geral` e `N1–N4` é explicada por `SemGrupo + OutroGrupo`.
- Se `Dif = SemGrupo?` for True, a diferença é 100% de tickets sem classificação de grupo (campo 8 vazio).

## JSON de Apoio
Além do relatório tabular, o script imprime um JSON com:
- `breakdown_por_grupo`: contagens de `com_nivel`, `sem_grupo`, `outro_grupo`, `total` por grupo.
- `soma_niveis`, `geral`, `dif_geral_menos_niveis`.
- `verificacao_sem_grupo`: detalha `dif`, `sem_grupo`, `outro_grupo` e flag `iguais` por grupo.

## Solução de Problemas
- Erro de autenticação: confirme `API_URL`, `APP_TOKEN` e `USER_TOKEN` em `backend/.env`.
- Zero resultados: verifique permissões do token e acesso ao endpoint `search/Ticket`.
- Colunas não fecham: valide se o GLPI está retornando o campo 8 corretamente (o script força `display[8]` e `display[12]`).

## Manutenção
- Este script é a referência única para auditoria de discrepâncias de níveis.
- Scripts auxiliares anteriores foram removidos por redundância.
- Para exportar CSV, pode ser adicionado um parâmetro futuro (não implementado neste momento).

## Exemplo de Execução
```
python backend\debug_output\breakdown_sem_grupo.py

===== Relatório de Discrepâncias (Geral vs Níveis) =====
Grupo               Geral      N1–N4   SemGrupo   OutroGrupo      Dif    SomaOK?  Dif = SemGrupo?   Dif = Sem+Outro?
...
TOTAL              10.518      6.811      1.972        1.735    3.707       True            False               True
```

Com isso, você pode somar manualmente as colunas e confirmar a consistência e a explicação das diferenças.