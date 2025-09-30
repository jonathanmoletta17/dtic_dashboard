# Relatório de Refatoração: Métricas Gerais

## 📋 Resumo Executivo

Este relatório detalha o processo de refatoração da lógica de **métricas gerais**, seguindo o mesmo padrão implementado com sucesso para o **ranking de técnicos**. O objetivo é extrair a lógica de negócios do endpoint `/metrics-gerais` para um módulo dedicado, melhorando a organização, manutenibilidade e testabilidade do código.

---

## 🎯 Objetivo da Refatoração

### Situação Atual
- Lógica de métricas gerais implementada diretamente no endpoint `/metrics-gerais` do `backend.py`
- Código misturado com lógica de API (violação do princípio de responsabilidade única)
- Dificuldade para testes unitários e reutilização

### Situação Desejada
- Lógica de negócios extraída para módulo `logic/metrics_logic.py`
- Endpoint `/metrics-gerais` apenas chama a função do módulo
- Código organizado, testável e reutilizável
- Padrão consistente com `ranking_logic.py`

---

## 📊 Análise da Implementação Atual

### Localização do Código Atual
**Arquivo:** `backend/backend.py` (linhas 185-208)

### Lógica Atual das Métricas Gerais
```python
@app.get("/metrics-gerais")
def get_metrics_gerais():
    """
    Métricas gerais: total de tickets, novos e fechados.
    Otimizado para usar apenas totalcount sem baixar dados.
    """
    try:
        headers = glpi_client.authenticate(API_URL, APP_TOKEN, USER_TOKEN)
        
        # Total de tickets - usando função otimizada
        total_tickets = get_count_only(headers)
        
        # Tickets novos (status=1) - apenas totalcount
        criteria_novos = [{"field": "12", "searchtype": "equals", "value": "1"}]
        count_novos = get_count_only(headers, criteria_novos)
        
        # Tickets fechados (status=6) - apenas totalcount
        criteria_fechados = [{"field": "12", "searchtype": "equals", "value": "6"}]
        count_fechados = get_count_only(headers, criteria_fechados)
        
        return {
            "total_tickets": total_tickets,
            "tickets_novos": count_novos,
            "tickets_fechados": count_fechados
        }
        
    except Exception as e:
        print(f"Erro em /metrics-gerais: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Função Auxiliar Utilizada
**Arquivo:** `backend/backend.py` (linhas 24-42)

```python
def get_count_only(headers, criteria=None):
    """Busca apenas o totalcount sem baixar dados."""
    import requests
    
    search_url = f"{API_URL}/search/Ticket"
    params = {
        'uid_cols': '1',
        'forcedisplay[0]': 'Ticket.id',
        'range': '0-0'  # Range mínimo para obter apenas totalcount
    }
    
    if criteria:
        for i, c in enumerate(criteria):
            for k, v in c.items():
                params[f'criteria[{i}][{k}]'] = v
    
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    
    return data.get('totalcount', 0)
```

---

## 🏗️ Plano de Refatoração

### 1. Criar Módulo `logic/metrics_logic.py`

**Estrutura do novo arquivo:**

```python
"""
Módulo de lógica de negócios para geração de métricas gerais do GLPI.
Implementação otimizada usando apenas totalcount para performance.
"""

import requests
from typing import Dict, Any

# Importa as funções robustas do cliente GLPI
from glpi_client import authenticate

# -- CONFIGURAÇÕES --
API_URL = "http://cau.ppiratini.intra.rs.gov.br/glpi/apirest.php"
APP_TOKEN = "aY3f9F5aNHJmY8op0vTE4koguiPwpEYANp1JULid"
USER_TOKEN = "TQdSxqg2e56PfF8ZJSX3iEJ1wCpHwhCkQJ2QtRnq"


def get_count_only(headers: Dict[str, str], api_url: str, criteria=None) -> int:
    """
    Busca apenas o totalcount sem baixar dados para otimizar performance.
    
    Args:
        headers: Headers com session-token
        api_url: URL base da API GLPI
        criteria: Critérios de filtro (opcional)
        
    Returns:
        int: Número total de registros que atendem aos critérios
    """
    search_url = f"{api_url}/search/Ticket"
    params = {
        'uid_cols': '1',
        'forcedisplay[0]': 'Ticket.id',
        'range': '0-0'  # Range mínimo para obter apenas totalcount
    }
    
    if criteria:
        for i, c in enumerate(criteria):
            for k, v in c.items():
                params[f'criteria[{i}][{k}]'] = v
    
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    
    return data.get('totalcount', 0)


def generate_general_metrics() -> Dict[str, Any]:
    """
    Gera as métricas gerais do sistema GLPI.
    
    Returns:
        Dict[str, Any]: Dicionário com as métricas:
        {
            "total_tickets": int,
            "tickets_novos": int,
            "tickets_fechados": int
        }
    """
    try:
        # Autenticação usando o cliente GLPI robusto
        session_headers = authenticate(API_URL, APP_TOKEN, USER_TOKEN)

        # 1. Total de tickets (sem filtros)
        total_tickets = get_count_only(session_headers, API_URL)
        
        # 2. Tickets novos (status=1)
        criteria_novos = [{"field": "12", "searchtype": "equals", "value": "1"}]
        count_novos = get_count_only(session_headers, API_URL, criteria_novos)
        
        # 3. Tickets fechados (status=6)
        criteria_fechados = [{"field": "12", "searchtype": "equals", "value": "6"}]
        count_fechados = get_count_only(session_headers, API_URL, criteria_fechados)
        
        return {
            "total_tickets": total_tickets,
            "tickets_novos": count_novos,
            "tickets_fechados": count_fechados
        }
        
    except Exception as e:
        print(f"❌ Erro ao gerar métricas gerais: {e}")
        return {
            "total_tickets": 0,
            "tickets_novos": 0,
            "tickets_fechados": 0
        }
```

### 2. Modificar o Endpoint no `backend.py`

**Alterações necessárias:**

#### 2.1. Adicionar Import
```python
# No topo do arquivo backend.py, adicionar:
from logic.metrics_logic import generate_general_metrics
```

#### 2.2. Simplificar o Endpoint
```python
@app.get("/metrics-gerais")
def get_metrics_gerais():
    """
    Métricas gerais: total de tickets, novos e fechados.
    Utiliza a lógica correta e validada do módulo metrics_logic.
    """
    try:
        metrics_data = generate_general_metrics()
        return metrics_data
        
    except Exception as e:
        print(f"❌ Erro em get_metrics_gerais: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### 2.3. Remover Código Obsoleto
- Remover a função `get_count_only` (linhas 24-42)
- Remover a função `get_total_tickets_count` (linhas 45-51)

---

## 📝 Mudanças Detalhadas

### Arquivos a Serem Criados

#### 1. `backend/logic/metrics_logic.py`
- **Novo arquivo** contendo toda a lógica de métricas gerais
- Função principal: `generate_general_metrics()`
- Função auxiliar: `get_count_only()`
- Configurações e imports necessários

### Arquivos a Serem Modificados

#### 1. `backend/backend.py`
**Linhas a serem alteradas:**

- **Linha ~10:** Adicionar import
  ```python
  from logic.metrics_logic import generate_general_metrics
  ```

- **Linhas 24-42:** Remover função `get_count_only`
- **Linhas 45-51:** Remover função `get_total_tickets_count`
- **Linhas 185-208:** Substituir endpoint completo por versão simplificada

**Estado final do endpoint:**
```python
@app.get("/metrics-gerais")
def get_metrics_gerais():
    """
    Métricas gerais: total de tickets, novos e fechados.
    Utiliza a lógica correta e validada do módulo metrics_logic.
    """
    try:
        metrics_data = generate_general_metrics()
        return metrics_data
        
    except Exception as e:
        print(f"❌ Erro em get_metrics_gerais: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🔍 Validações Necessárias

### 1. Validação de Funcionalidade

#### 1.1. Teste do Módulo Isolado
```bash
# Criar script de teste
python -c "
from backend.logic.metrics_logic import generate_general_metrics
import json
result = generate_general_metrics()
print('Métricas Gerais:')
print(json.dumps(result, indent=2))
"
```

**Resultado esperado:**
```json
{
  "total_tickets": 10396,
  "tickets_novos": 5,
  "tickets_fechados": 6891
}
```

#### 1.2. Teste do Endpoint Refatorado
```bash
# Testar endpoint via curl
curl -X GET "http://localhost:8000/metrics-gerais" -H "accept: application/json"
```

**Resultado esperado:** Mesmo JSON do teste anterior

#### 1.3. Teste de Performance
```bash
# Medir tempo de resposta
time curl -X GET "http://localhost:8000/metrics-gerais"
```

**Resultado esperado:** Tempo similar ao atual (2-4 segundos)

### 2. Validação de Integração

#### 2.1. Teste do Dashboard
- Abrir dashboard em `http://localhost:8050`
- Verificar se métricas carregam automaticamente
- Confirmar valores corretos nos cards superiores

#### 2.2. Teste de Navegação
- Navegar entre páginas do dashboard
- Usar botão "voltar" do navegador
- Verificar se métricas permanecem consistentes

### 3. Validação de Erro

#### 3.1. Teste com Backend Indisponível
```bash
# Parar backend temporariamente
# Verificar se dashboard mostra valores zerados sem quebrar
```

#### 3.2. Teste com GLPI Indisponível
- Simular falha na conexão GLPI
- Verificar se retorna valores zerados
- Confirmar que não há exceções não tratadas

---

## 📊 Comparação: Antes vs Depois

### Antes da Refatoração

**Estrutura:**
```
backend/
├── backend.py (323 linhas)
│   ├── get_count_only()           # Lógica de negócios
│   ├── get_total_tickets_count()  # Lógica de negócios
│   └── get_metrics_gerais()       # Endpoint + lógica
```

**Problemas:**
- ❌ Lógica misturada com API
- ❌ Difícil de testar isoladamente
- ❌ Código duplicado (get_count_only)
- ❌ Violação do princípio de responsabilidade única

### Depois da Refatoração

**Estrutura:**
```
backend/
├── backend.py (~280 linhas)
│   └── get_metrics_gerais()       # Apenas endpoint
├── logic/
│   ├── ranking_logic.py           # Lógica de ranking
│   └── metrics_logic.py           # Lógica de métricas
│       ├── get_count_only()
│       └── generate_general_metrics()
```

**Benefícios:**
- ✅ Separação clara de responsabilidades
- ✅ Código testável isoladamente
- ✅ Padrão consistente com ranking
- ✅ Facilita manutenção e evolução
- ✅ Reduz tamanho do backend.py

---

## 🚀 Plano de Implementação

### Fase 1: Preparação (5 min)
1. ✅ Criar diretório `backend/logic/` (se não existir)
2. ✅ Criar arquivo `backend/logic/metrics_logic.py`
3. ✅ Implementar função `generate_general_metrics()`

### Fase 2: Refatoração (10 min)
1. ✅ Modificar `backend/backend.py`:
   - Adicionar import
   - Simplificar endpoint
   - Remover funções obsoletas
2. ✅ Testar funcionamento básico

### Fase 3: Validação (15 min)
1. ✅ Executar testes de funcionalidade
2. ✅ Validar integração com dashboard
3. ✅ Testar cenários de erro
4. ✅ Verificar performance

### Fase 4: Documentação (5 min)
1. ✅ Atualizar este relatório com resultados
2. ✅ Documentar mudanças no CHANGELOG.md

**Tempo total estimado:** 35 minutos

---

## 📈 Métricas de Sucesso

### Critérios de Aceitação
- ✅ Endpoint `/metrics-gerais` retorna mesmos dados
- ✅ Dashboard carrega métricas automaticamente
- ✅ Performance mantida (tempo < 5s)
- ✅ Tratamento de erros funcional
- ✅ Código organizado e testável

### Indicadores de Qualidade
- ✅ Redução de ~40 linhas no `backend.py`
- ✅ Separação clara de responsabilidades
- ✅ Padrão consistente com `ranking_logic.py`
- ✅ Facilidade para testes unitários
- ✅ Reutilização da lógica em outros contextos

---

## 🔄 Próximos Passos Recomendados

### Imediatos (Pós-Refatoração)
1. **Implementar cache de 5 minutos** para otimizar performance
2. **Criar testes unitários** para `metrics_logic.py`
3. **Monitorar logs** para identificar possíveis problemas

### Futuras Melhorias
1. **Refatorar `/status-niveis`** seguindo o mesmo padrão
2. **Refatorar `/tickets-novos`** seguindo o mesmo padrão
3. **Implementar cache centralizado** para todos os módulos
4. **Adicionar métricas de observabilidade** (tempo de resposta, taxa de erro)

---

## 📋 Checklist de Implementação

### Preparação
- [ ] Verificar se diretório `backend/logic/` existe
- [ ] Criar arquivo `backend/logic/metrics_logic.py`
- [ ] Implementar função `generate_general_metrics()`
- [ ] Implementar função auxiliar `get_count_only()`

### Refatoração
- [ ] Adicionar import em `backend/backend.py`
- [ ] Simplificar endpoint `/metrics-gerais`
- [ ] Remover função `get_count_only` obsoleta
- [ ] Remover função `get_total_tickets_count` obsoleta

### Validação
- [ ] Testar módulo isoladamente
- [ ] Testar endpoint refatorado
- [ ] Validar integração com dashboard
- [ ] Testar cenários de erro
- [ ] Verificar performance

### Documentação
- [ ] Atualizar CHANGELOG.md
- [ ] Documentar mudanças no README (se necessário)
- [ ] Marcar tarefa como concluída

---

## 📞 Suporte e Contato

Em caso de dúvidas ou problemas durante a implementação:
1. Verificar logs do backend (`uvicorn` output)
2. Testar endpoints individualmente com `curl`
3. Validar autenticação GLPI
4. Consultar implementação de referência em `ranking_logic.py`

---

**Relatório gerado em:** $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")  
**Versão:** 1.0  
**Status:** Pronto para implementação