# Relatório de Auditoria - Erros nos Endpoints da API GLPI

## 📋 Resumo Executivo

**Status:** ❌ CRÍTICO - Dados zerados em produção  
**Data:** 30/09/2025  
**Problema:** Endpoints retornando valores zerados após refatoração dos campos GLPI  

## 🔍 Análise do Problema

### Sintomas Observados
```
🔍 Estratégia Final: Lendo todos os Group_User e filtrando em Python...
   - 0 usuários mapeados para os níveis de interesse.
INFO: 127.0.0.1:56685 - "GET /api/v1/metrics-gerais HTTP/1.1" 200 OK
```

### Causa Raiz Identificada

**PROBLEMA PRINCIPAL:** Incompatibilidade entre `forcedisplay` e estrutura de dados retornada

#### Evidências dos Testes:

1. **Teste com nomes de campos (FUNCIONAVA ANTES):**
   ```python
   forcedisplay=['users_id', 'groups_id']
   # Resultado: 1271 registros, mas primeiro registro = [] (vazio)
   ```

2. **Teste com IDs numéricos (IMPLEMENTAÇÃO ATUAL):**
   ```python
   forcedisplay=['2', '3']  
   # Resultado: 1271 registros, primeiro registro = {'Group_User.id': 2, 'Group_User.is_dynamic': 1}
   ```

## 🚨 Problemas Identificados

### 1. Mapeamento de Campos Incorreto
- **Campo '2':** Retorna `Group_User.id` (ID da associação), NÃO `users_id`
- **Campo '3':** Retorna `Group_User.is_dynamic`, NÃO `groups_id`
- **Impacto:** 100% dos usuários não são mapeados corretamente

### 2. Estrutura de Dados Inconsistente
```python
# ESPERADO (baseado no JSON de debug):
{
    "users_id": 167,
    "groups_id": 89
}

# ATUAL (com IDs numéricos):
{
    "Group_User.id": 2,
    "Group_User.is_dynamic": 1
}
```

### 3. Lógica de Filtragem Quebrada
```python
# Código atual procura por:
user_id = link.get('2')      # Retorna Group_User.id (2)
group_id = link.get('3')     # Retorna Group_User.is_dynamic (1)

# Resultado: group_id nunca está em group_mapping = {89: "N1", 90: "N2", 91: "N3", 92: "N4"}
```

## 📊 Comparação: Antes vs Depois

### ANTES (Funcionando)
```python
# Arquivo: debug_usuarios_grupos.json
{
    "users_id": 167,
    "groups_id": 89,  # ✅ Mapeia para N1
    "is_dynamic": 0
}
```

### DEPOIS (Quebrado)
```python
# Implementação atual
{
    "Group_User.id": 2,        # ❌ Não é users_id
    "Group_User.is_dynamic": 1 # ❌ Não é groups_id
}
```

## 🔧 Soluções Recomendadas

### Opção 1: Reverter para Nomes de Campos (RECOMENDADA)
```python
# Voltar para a implementação que funcionava
forcedisplay=['users_id', 'groups_id']
```

### Opção 2: Identificar IDs Corretos
- Executar debug completo para encontrar os IDs numéricos reais
- Campo para `users_id`: TBD
- Campo para `groups_id`: TBD

### Opção 3: Busca Sem forcedisplay
```python
# Buscar todos os campos e filtrar em Python
all_group_user_links = glpi_client.search_paginated(
    session_headers, api_url, "Group_User"
    # Sem forcedisplay - retorna todos os campos
)
```

## 📈 Impacto nos Endpoints

| Endpoint | Status | Dados Retornados |
|----------|--------|------------------|
| `/api/v1/metrics-gerais` | ❌ | `{"novos":0,"em_progresso":0,"pendentes":0,"resolvidos":0}` |
| `/api/v1/status-niveis` | ❌ | Todos os níveis N1-N4 com valores 0 |
| `/api/v1/ranking-tecnicos` | ✅ | Funcionando (usa lógica diferente) |
| `/api/v1/tickets-novos` | ✅ | Funcionando |

## 🎯 Próximos Passos

1. **URGENTE:** Reverter `forcedisplay` para nomes de campos
2. **TESTE:** Validar com dados reais em ambiente de desenvolvimento
3. **DEPLOY:** Aplicar correção em produção
4. **MONITORAMENTO:** Verificar logs por 24h após correção

## 📝 Lições Aprendidas

1. **Sempre testar com dados reais** antes de fazer deploy
2. **Manter backup da implementação funcionando**
3. **IDs numéricos do GLPI não são consistentes** entre versões/instalações
4. **Nomes de campos são mais estáveis** que IDs numéricos

---

**Responsável:** Equipe de Desenvolvimento  
**Prioridade:** CRÍTICA  
**Estimativa de Correção:** 30 minutos