# Guia: Como Construir Métricas por Nível Usando a API REST do GLPI

> Esta explicação é baseada no padrão funcional do monolito (GLPIService), nos problemas identificados no seu `metrics_logic.py` atual, e nos requisitos de negócio para exibir as métricas por status e por nível (N1, N2, N3, N4).

## 1. Métricas Gerais vs. Métricas por Nível de Atendimento

### Métricas Gerais
*   **O que são:** Totais de tickets por status (Novo, Em Progresso, Pendente, Resolvido, Fechado) sem separar por nível.
*   **Como buscar:** Filtrar apenas pelo campo de status (`status`/campo `12`) em todos os tickets.
*   **Exemplo de critério para "Novo":**
    ```json
    {
      "criteria": [
        {"field": "12", "searchtype": "equals", "value": "1"}
      ]
    }
    ```

### Métricas por Nível
*   **O que são:** Totais de tickets por status (os mesmos dos gerais), separados por nível de atendimento (N1, N2, N3, N4).
*   **Como buscar:** Para cada nível, filtrar por dois campos simultaneamente:
    1.  Pelo campo de **hierarquia do ticket** (campo `8`), onde o valor contém "N1", "N2", etc.
    2.  Pelo campo de **status** (campo `12`), igual ao status desejado.
*   **Exemplo de critério para "Novo" no N2:**
    ```json
    {
      "criteria": [
        {"field": "8", "searchtype": "contains", "value": "N2"},
        {"field": "12", "searchtype": "equals", "value": "1"}
      ]
    }
    ```

## 2. Estrutura e Parâmetros da Requisição

### Campos Fundamentais
*   **Campo 8:** Hierarquia do ticket (string que contém "N1", "N2", etc).
*   **Campo 12:** Status do ticket (inteiro conforme mapeamento de status do GLPI).
*   **(Opcional) Data:** Se quiser filtrar por data de criação (campo `15`) ou modificação (campo `19`).

### Estrutura dos Parâmetros GET para `/search/Ticket`
Para cada combinação de nível e status, os parâmetros seriam:
*   `criteria[0][field]=8`
*   `criteria[0][searchtype]=contains`
*   `criteria[0][value]=N1` (ou N2, N3, N4)
*   `criteria[1][link]=AND`
*   `criteria[1][field]=12`
*   `criteria[1][searchtype]=equals`
*   `criteria[1][value]=1` (1=Novo, 2=Processando, etc)

**Exemplo para N3/Processando (atribuído):**
```
criteria[0][field]=8
criteria[0][searchtype]=contains
criteria[0][value]=N3
criteria[1][link]=AND
criteria[1][field]=12
criteria[1][searchtype]=equals
criteria[1][value]=2
range=0-0
forcedisplay[0]=8
forcedisplay[1]=12
```

### Como Obter o Total de Tickets
O GLPI retorna o total de duas formas:
1.  No header da resposta, no campo `Content-Range` (ex: `Content-Range: 0-0/25`), onde o número após a barra é o total.
2.  No corpo do JSON, no campo `totalcount`.

## 3. Estrutura do Dicionário de Resultado
O resultado para o dashboard deve ser um dicionário com a seguinte estrutura:
```python
{
    "n1": {"Novo": 10, "Processando (atribuído)": 5, "Pendente": 3, ...},
    "n2": {"Novo": 7, ...},
    "n3": {...},
    "n4": {...}
}
```
**Importante:**
*   Os nomes dos status devem ser exatamente os mesmos usados nas métricas gerais.
*   Os totais devem ser a soma correta dos tickets por status e por nível.

## 4. Passos Detalhados para Implementação

### A. Mapeamento de Status (Ajuste conforme seu GLPI)
Verifique seu mapeamento real. Um exemplo comum é:
```python
status_map = {
    "Novo": 1,
    "Processando (atribuído)": 2,
    "Processando (planejado)": 3,
    "Pendente": 4,
    "Solucionado": 5,
    "Fechado": 6,
}
```

### B. Loop de Consulta
1.  Para cada nível (`N1`, `N2`, `N3`, `N4`):
2.  Para cada status:
    *   Faça a requisição a `/search/Ticket` com os parâmetros combinando hierarquia (campo `8`) e status (campo `12`).
    *   Extraia o total do header `Content-Range` ou do JSON.
    *   Armazene o valor no dicionário de resultado.

### C. Função de Apoio para Contar Tickets
Implemente no seu `glpi_client`:
```python
def count_tickets(api_url, session_headers, criteria):
    # Faz GET para /search/Ticket com os critérios informados e range=0-0
    # Retorna o total do Content-Range ou do JSON
```

### D. (Opcional) Otimização
É possível consultar múltiplos níveis/status em uma única query usando `OR`, mas a abordagem mais segura e simples é fazer uma consulta para cada combinação.

## 5. Checklist para Implementação

*   [ ] Verificar se o **campo 8** existe e contém as strings dos níveis corretos ("N1", "N2", etc) nos tickets.
*   [ ] Garantir que o `status_map` está correto e cobre todos os status usados nas métricas gerais.
*   [ ] Implementar a função para contar tickets pelo endpoint `/search/Ticket`, usando critérios de campo `8` e `12`.
*   [ ] Montar o dicionário de métricas por nível e por status exatamente como nas métricas gerais.
*   [ ] Logar os parâmetros de cada requisição e o resultado retornado para depuração.
*   [ ] Certificar-se de que está extraindo o total do header `Content-Range` ou do campo `totalcount`.
*   [ ] Testar manualmente no Postman/Insomnia as queries para cada nível e status.
*   [ ] Garantir que a função é chamada pelo dashboard e retorna o JSON no formato esperado.

## 6. Exemplo Didático (Pseudocódigo)

```python
result = {}
for nivel in ["N1", "N2", "N3", "N4"]:
    result[nivel.lower()] = {}
    for status_name, status_id in status_map.items():
        criteria = [
            {"field": "8", "searchtype": "contains", "value": nivel},
            {"field": "12", "searchtype": "equals", "value": str(status_id)},
        ]
        total = count_tickets(api_url, session_headers, criteria)
        result[nivel.lower()][status_name] = total
```

## Resumo

*   Métricas por nível são obtidas filtrando tickets pelo campo de **hierarquia (campo 8)** e **status (campo 12)**.
*   Para cada nível e status, faça uma query e extraia o total.
*   O resultado deve ser um dicionário igual ao das métricas gerais, mas separado por nível.
*   Compare os campos e IDs do seu GLPI para garantir que a lógica está correta.
*   Implemente funções de apoio no seu `glpi_client` para facilitar a contagem via API.
*   Teste e logue cada query e resposta.

> Se o time seguir essa estrutura, conseguirá implementar corretamente a busca e exibição das métricas por nível de atendimento no dashboard, com os mesmos status das métricas gerais e totalizações corretas!