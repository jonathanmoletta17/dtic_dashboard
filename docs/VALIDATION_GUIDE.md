# Guia de Validação e Testes - Dashboard DTIC

## 📋 Visão Geral

Este documento fornece critérios específicos de validação e procedimentos de teste para cada etapa da implementação do dashboard, garantindo qualidade e consistência em todas as mudanças.

## 🎯 Princípios de Validação

### Critérios Fundamentais:
1. **Funcionalidade**: Todos os recursos devem funcionar conforme especificado
2. **Visual**: Design deve corresponder ao original
3. **Performance**: Não deve degradar a performance existente
4. **Responsividade**: Deve funcionar em todos os dispositivos
5. **Acessibilidade**: Deve atender padrões básicos de acessibilidade

---

## 🧪 Validação por Etapa

### Etapa 1.1: Preparação do Ambiente

#### ✅ Critérios de Validação:
- [ ] **Backup criado**: Branch `backup/current-implementation` existe
- [ ] **Dependências instaladas**: `lucide-react` versão correta
- [ ] **Aplicação funcional**: `npm run dev` executa sem erros
- [ ] **Git limpo**: `git status` não mostra arquivos não commitados

#### 🧪 Comandos de Teste:
```bash
# Verificar backup
git branch | grep backup/current-implementation

# Verificar dependências
cd frontend
npm list lucide-react
npm list tailwindcss

# Testar aplicação
npm run dev
# Aguardar 10 segundos e verificar se carrega sem erros

# Verificar git
git status
```

#### 🚨 Critérios de Falha:
- Aplicação não inicia
- Erros de dependência no console
- Branch de backup não existe

---

### Etapa 1.2: Restauração do Header

#### ✅ Critérios de Validação:
- [ ] **Gradiente visível**: Background azul com gradiente
- [ ] **Ícone BarChart3**: Aparece à esquerda com cor azul clara
- [ ] **Título correto**: "Dashboard DTIC" em fonte grande
- [ ] **Subtítulo presente**: "Sistema de Monitoramento de Tickets"
- [ ] **Timestamp funcional**: Data/hora atual à direita
- [ ] **Ícone RefreshCw**: Aparece à direita
- [ ] **Responsividade**: Layout se adapta em mobile

#### 🧪 Comandos de Teste:
```bash
# Iniciar aplicação
npm run dev

# Abrir DevTools (F12)
# Verificar console - não deve ter erros relacionados ao header

# Testar responsividade
# Redimensionar janela para 375px de largura
# Verificar se elementos se reorganizam adequadamente
```

#### 📱 Teste Visual:
1. **Desktop (1920x1080)**:
   - Header ocupa largura total
   - Elementos alinhados horizontalmente
   - Gradiente visível de azul escuro para azul médio

2. **Tablet (768x1024)**:
   - Layout mantém estrutura
   - Texto permanece legível
   - Espaçamentos proporcionais

3. **Mobile (375x667)**:
   - Elementos podem empilhar verticalmente
   - Texto não trunca
   - Ícones mantêm tamanho adequado

#### 🚨 Critérios de Falha:
- Gradiente não aparece
- Ícones não carregam
- Timestamp não atualiza
- Layout quebra em mobile
- Erros no console

---

### Etapa 1.3: Cards de Estatísticas Gerais

#### ✅ Critérios de Validação:
- [ ] **Cards com gradiente**: Laranja-vermelho (Pendentes), Verde-esmeralda (Resolvidos)
- [ ] **Ícones corretos**: Clock (Pendentes), CheckCircle (Resolvidos)
- [ ] **Animação hover**: Cards fazem scale ao passar mouse
- [ ] **Dados da API**: Valores reais são exibidos
- [ ] **Métricas de tendência**: Percentuais aparecem com ícone TrendingUp
- [ ] **Layout responsivo**: Grid se adapta ao tamanho da tela

#### 🧪 Comandos de Teste:
```bash
# Testar API
curl http://localhost:8000/api/stats/general
# Deve retornar JSON com pending e resolved

# Verificar no browser
npm run dev
# Aguardar carregamento dos dados
# Verificar se números não são 0 (assumindo que há dados)
```

#### 📱 Teste de Interação:
1. **Hover Effect**:
   - Passar mouse sobre cada card
   - Verificar animação de escala suave
   - Transição deve durar ~300ms

2. **Responsividade**:
   - Desktop: 4 colunas (se houver 4 cards)
   - Tablet: 2 colunas
   - Mobile: 1 coluna

#### 🎨 Teste Visual:
1. **Card Pendentes**:
   - Gradiente laranja para vermelho
   - Ícone Clock branco
   - Texto em tons de laranja claro
   - Número grande e bold

2. **Card Resolvidos**:
   - Gradiente verde para esmeralda
   - Ícone CheckCircle branco
   - Texto em tons de verde claro
   - Número grande e bold

#### 🚨 Critérios de Falha:
- Gradientes não aparecem
- Animação hover não funciona
- Dados não carregam da API
- Layout quebra em diferentes telas

---

### Etapa 2.1: Seções de Nível (N1-N4)

#### ✅ Critérios de Validação:
- [ ] **4 cards de nível**: N1, N2, N3, N4 renderizam
- [ ] **Headers coloridos**: Cada nível com gradiente diferente
- [ ] **Grid 2x2 interno**: 4 estatísticas por nível organizadas em quadrantes
- [ ] **Ícones por status**: Plus (Novos), Clock (Progresso), AlertCircle (Pendentes), CheckCircle (Resolvidos)
- [ ] **Cores temáticas**: Azul (Novos), Amarelo (Progresso), Laranja (Pendentes), Verde (Resolvidos)
- [ ] **Dados da API**: Valores reais para cada nível e status
- [ ] **Responsividade**: Layout se adapta adequadamente

#### 🧪 Comandos de Teste:
```bash
# Testar API de níveis
curl http://localhost:8000/api/stats/levels
# Deve retornar array com 4 níveis

# Verificar estrutura de dados
# Cada nível deve ter: level, new, in_progress, pending, resolved
```

#### 📊 Teste de Dados:
1. **Verificar mapeamento**:
   - N1: Primeiro item do array
   - N2: Segundo item do array
   - N3: Terceiro item do array
   - N4: Quarto item do array

2. **Verificar valores**:
   - Todos os números devem ser >= 0
   - Soma deve fazer sentido com totais gerais

#### 🎨 Teste Visual por Nível:
1. **Header de cada nível**:
   - N1: Gradiente azul
   - N2: Gradiente roxo
   - N3: Gradiente índigo
   - N4: Gradiente teal
   - Ícone Users branco à direita

2. **Grid interno (2x2)**:
   - Superior esquerdo: Novos (azul)
   - Superior direito: Em Progresso (amarelo)
   - Inferior esquerdo: Pendentes (laranja)
   - Inferior direito: Resolvidos (verde)

#### 📱 Teste de Responsividade:
- **Desktop (XL)**: 4 colunas
- **Desktop (LG)**: 2 colunas
- **Mobile**: 1 coluna

#### 🚨 Critérios de Falha:
- Menos de 4 cards aparecem
- Gradientes não diferem entre níveis
- Grid interno não forma 2x2
- Ícones não aparecem ou estão incorretos
- Dados não carregam

---

### Etapa 2.2: Ranking de Técnicos

#### ✅ Critérios de Validação:
- [ ] **Ícone Trophy**: Aparece no título em amarelo
- [ ] **Indicador temporal**: "Últimos 30 dias" com ícone Calendar
- [ ] **Posições coloridas**: 1º (ouro), 2º (prata), 3º (bronze), demais (azul)
- [ ] **Coroa no 1º lugar**: Ícone Crown no primeiro colocado
- [ ] **Avatares com iniciais**: Círculos com gradiente e iniciais do nome
- [ ] **Hover effect**: Background muda ao passar mouse
- [ ] **Dados da API**: Nomes e números de tickets corretos

#### 🧪 Comandos de Teste:
```bash
# Testar API de ranking
curl http://localhost:8000/api/ranking/technicians
# Deve retornar array ordenado por resolved_tickets
```

#### 🎨 Teste Visual:
1. **Posições**:
   - 1º lugar: Círculo amarelo com coroa
   - 2º lugar: Círculo cinza com "2"
   - 3º lugar: Círculo laranja com "3"
   - Demais: Círculo azul com número

2. **Avatares**:
   - Círculo com gradiente azul-roxo
   - Iniciais do nome em branco
   - Tamanho consistente

3. **Informações**:
   - Nome em negrito
   - "Técnico de Suporte" em cinza
   - Número de tickets em destaque

#### 🖱️ Teste de Interação:
- Hover sobre cada item
- Background deve mudar de cinza claro para cinza médio
- Transição suave

#### 🚨 Critérios de Falha:
- Posições não têm cores corretas
- Coroa não aparece no 1º lugar
- Avatares não mostram iniciais
- Hover effect não funciona

---

### Etapa 2.3: Tickets Novos

#### ✅ Critérios de Validação:
- [ ] **Ícone Ticket**: Aparece no título em azul
- [ ] **Botão "Ver todos"**: Com ícone ChevronRight à direita
- [ ] **IDs formatados**: Prefixo # com fonte monospace
- [ ] **Status badges**: Fundo verde claro com texto verde escuro
- [ ] **Informações completas**: Título, descrição, responsável, data
- [ ] **Hover effect**: Sombra aumenta ao passar mouse
- [ ] **Dados da API**: Tickets reais são exibidos

#### 🧪 Comandos de Teste:
```bash
# Testar API de tickets
curl http://localhost:8000/api/tickets/new
# Deve retornar array com tickets novos
```

#### 🎨 Teste Visual:
1. **Header da seção**:
   - Ícone Ticket azul
   - Título "Tickets Novos"
   - Botão "Ver todos" à direita

2. **Cards de ticket**:
   - Borda cinza clara
   - ID com fundo azul claro
   - Badge "Novo" verde
   - Data à direita
   - Título em negrito
   - Descrição truncada
   - Ícone User + responsável
   - Seta à direita

#### 🖱️ Teste de Interação:
1. **Hover nos cards**:
   - Sombra deve aumentar
   - Transição suave

2. **Botão "Ver todos"**:
   - Cor muda ao hover
   - Cursor pointer

#### 🚨 Critérios de Falha:
- IDs não têm formatação especial
- Status badges não aparecem
- Hover effect não funciona
- Informações incompletas

---

## 🔧 Ferramentas de Validação

### Validação Automática:
```bash
# Lint check
npm run lint

# Type check
npm run type-check

# Build test
npm run build

# Unit tests (se existirem)
npm test
```

### Validação Manual:
```bash
# Performance check
# Abrir DevTools > Lighthouse
# Executar audit para Performance, Accessibility, Best Practices

# Bundle size check
npm run build
# Verificar tamanho dos arquivos em dist/
```

### Validação de Responsividade:
```bash
# Chrome DevTools
# F12 > Toggle device toolbar
# Testar em:
# - iPhone SE (375x667)
# - iPad (768x1024)
# - Desktop (1920x1080)
```

---

## 📊 Métricas de Qualidade

### Performance:
- **Lighthouse Score**: > 90
- **First Contentful Paint**: < 2s
- **Largest Contentful Paint**: < 3s
- **Bundle Size**: < 1MB

### Acessibilidade:
- **Contraste**: Mínimo AA (4.5:1)
- **Navegação por teclado**: Funcional
- **Screen readers**: Compatível
- **Alt texts**: Presentes em ícones importantes

### Funcionalidade:
- **API Response Time**: < 500ms
- **Error Rate**: 0%
- **Loading States**: Implementados
- **Error Handling**: Graceful

---

## 🚨 Plano de Rollback

### Se validação falhar:
1. **Identificar** o problema específico
2. **Reverter** para commit anterior:
   ```bash
   git reset --hard HEAD~1
   ```
3. **Analisar** logs e erros
4. **Corrigir** implementação
5. **Re-testar** antes de prosseguir

### Comandos de emergência:
```bash
# Rollback completo para backup
git checkout backup/current-implementation

# Rollback específico de arquivo
git checkout HEAD~1 -- frontend/src/App.tsx

# Limpar cache e reinstalar
rm -rf node_modules package-lock.json
npm install
```

---

## 📋 Checklist de Validação Completa

### Antes de cada etapa:
- [ ] Ambiente preparado
- [ ] Backup criado
- [ ] Dependências verificadas

### Durante implementação:
- [ ] Código seguindo padrões
- [ ] Testes incrementais
- [ ] Console sem erros

### Após cada etapa:
- [ ] Todos os critérios atendidos
- [ ] Testes visuais aprovados
- [ ] Performance mantida
- [ ] Responsividade validada

### Finalização:
- [ ] Validação completa executada
- [ ] Documentação atualizada
- [ ] Commit com mensagem descritiva
- [ ] Ready para próxima etapa

---

**Última Atualização**: $(Get-Date -Format "dd/MM/yyyy HH:mm")  
**Status**: Guia Completo ✅