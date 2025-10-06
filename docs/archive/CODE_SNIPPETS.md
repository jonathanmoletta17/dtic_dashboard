# Snippets de Código - Dashboard DTIC

## 📋 Visão Geral

Este documento contém todos os snippets de código organizados por seção, prontos para implementação direta. Cada snippet inclui imports necessários e pode ser copiado e colado diretamente no arquivo `App.tsx`.

---

## 📦 Imports Necessários

### Imports Completos para App.tsx:
```tsx
import React, { useState, useEffect, useMemo } from 'react';
import {
  BarChart3,
  RefreshCw,
  Clock,
  CheckCircle,
  TrendingUp,
  Users,
  Plus,
  AlertCircle,
  Trophy,
  Calendar,
  Crown,
  Ticket,
  ChevronRight,
  User
} from 'lucide-react';
import { apiService } from './services/api';
import type { GeneralStats, LevelStats, TechnicianRanking, NewTicket } from './types/api';
```

---

## 🎯 Seção 1: Header

### Header Completo:
```tsx
{/* Header com gradiente e elementos visuais */}
<div className="bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900 text-white p-6 shadow-lg">
  <div className="flex items-center justify-between">
    <div className="flex items-center space-x-4">
      <div className="bg-white/10 p-3 rounded-full backdrop-blur-sm">
        <BarChart3 className="h-8 w-8 text-blue-200" />
      </div>
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard DTIC</h1>
        <p className="text-blue-200 text-sm font-medium">
          Sistema de Monitoramento de Tickets
        </p>
      </div>
    </div>
    <div className="flex items-center space-x-6">
      <div className="text-right">
        <p className="text-sm text-blue-200">Última atualização</p>
        <p className="text-lg font-semibold">
          {new Date().toLocaleString('pt-BR')}
        </p>
      </div>
      <div className="bg-white/10 p-2 rounded-lg backdrop-blur-sm">
        <RefreshCw className="h-6 w-6 text-blue-200" />
      </div>
    </div>
  </div>
</div>
```

### Header Responsivo (Versão Mobile):
```tsx
{/* Header responsivo para mobile */}
<div className="bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900 text-white p-4 md:p-6 shadow-lg">
  <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
    <div className="flex items-center space-x-3 md:space-x-4">
      <div className="bg-white/10 p-2 md:p-3 rounded-full backdrop-blur-sm">
        <BarChart3 className="h-6 w-6 md:h-8 md:w-8 text-blue-200" />
      </div>
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Dashboard DTIC</h1>
        <p className="text-blue-200 text-xs md:text-sm font-medium">
          Sistema de Monitoramento de Tickets
        </p>
      </div>
    </div>
    <div className="flex items-center justify-between md:space-x-6">
      <div className="text-left md:text-right">
        <p className="text-xs md:text-sm text-blue-200">Última atualização</p>
        <p className="text-sm md:text-lg font-semibold">
          {new Date().toLocaleString('pt-BR')}
        </p>
      </div>
      <div className="bg-white/10 p-2 rounded-lg backdrop-blur-sm">
        <RefreshCw className="h-5 w-5 md:h-6 md:w-6 text-blue-200" />
      </div>
    </div>
  </div>
</div>
```

---

## 📊 Seção 2: Cards de Estatísticas Gerais

### Cards Completos:
```tsx
{/* Cards de estatísticas gerais com gradientes e animações */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
  {/* Card Pendentes */}
  <div className="bg-gradient-to-br from-orange-500 to-red-600 p-6 rounded-xl shadow-lg text-white transform hover:scale-105 transition-all duration-300">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-orange-100 text-sm font-medium uppercase tracking-wide">
          Pendentes
        </p>
        <p className="text-3xl font-bold mt-2">{generalStats?.pending || 0}</p>
        <div className="flex items-center mt-2">
          <TrendingUp className="h-4 w-4 text-orange-200 mr-1" />
          <span className="text-orange-200 text-sm">+12% esta semana</span>
        </div>
      </div>
      <div className="bg-white/20 p-3 rounded-full">
        <Clock className="h-8 w-8 text-orange-100" />
      </div>
    </div>
  </div>
  
  {/* Card Resolvidos */}
  <div className="bg-gradient-to-br from-green-500 to-emerald-600 p-6 rounded-xl shadow-lg text-white transform hover:scale-105 transition-all duration-300">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-green-100 text-sm font-medium uppercase tracking-wide">
          Resolvidos
        </p>
        <p className="text-3xl font-bold mt-2">{generalStats?.resolved || 0}</p>
        <div className="flex items-center mt-2">
          <TrendingUp className="h-4 w-4 text-green-200 mr-1" />
          <span className="text-green-200 text-sm">+8% esta semana</span>
        </div>
      </div>
      <div className="bg-white/20 p-3 rounded-full">
        <CheckCircle className="h-8 w-8 text-green-100" />
      </div>
    </div>
  </div>

  {/* Card Em Progresso (opcional) */}
  <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-6 rounded-xl shadow-lg text-white transform hover:scale-105 transition-all duration-300">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-blue-100 text-sm font-medium uppercase tracking-wide">
          Em Progresso
        </p>
        <p className="text-3xl font-bold mt-2">{generalStats?.in_progress || 0}</p>
        <div className="flex items-center mt-2">
          <TrendingUp className="h-4 w-4 text-blue-200 mr-1" />
          <span className="text-blue-200 text-sm">+5% esta semana</span>
        </div>
      </div>
      <div className="bg-white/20 p-3 rounded-full">
        <Clock className="h-8 w-8 text-blue-100" />
      </div>
    </div>
  </div>

  {/* Card Total (opcional) */}
  <div className="bg-gradient-to-br from-purple-500 to-pink-600 p-6 rounded-xl shadow-lg text-white transform hover:scale-105 transition-all duration-300">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-purple-100 text-sm font-medium uppercase tracking-wide">
          Total
        </p>
        <p className="text-3xl font-bold mt-2">
          {(generalStats?.pending || 0) + (generalStats?.resolved || 0) + (generalStats?.in_progress || 0)}
        </p>
        <div className="flex items-center mt-2">
          <TrendingUp className="h-4 w-4 text-purple-200 mr-1" />
          <span className="text-purple-200 text-sm">+15% esta semana</span>
        </div>
      </div>
      <div className="bg-white/20 p-3 rounded-full">
        <BarChart3 className="h-8 w-8 text-purple-100" />
      </div>
    </div>
  </div>
</div>
```

### Card Individual (Componente Reutilizável):
```tsx
{/* Componente de card reutilizável */}
const StatCard = React.memo(({ 
  title, 
  value, 
  trend, 
  icon: Icon, 
  gradientFrom, 
  gradientTo, 
  textColor 
}) => (
  <div className={`bg-gradient-to-br ${gradientFrom} ${gradientTo} p-6 rounded-xl shadow-lg text-white transform hover:scale-105 transition-all duration-300`}>
    <div className="flex items-center justify-between">
      <div>
        <p className={`${textColor} text-sm font-medium uppercase tracking-wide`}>
          {title}
        </p>
        <p className="text-3xl font-bold mt-2">{value}</p>
        <div className="flex items-center mt-2">
          <TrendingUp className={`h-4 w-4 ${textColor} mr-1`} />
          <span className={`${textColor} text-sm`}>{trend}</span>
        </div>
      </div>
      <div className="bg-white/20 p-3 rounded-full">
        <Icon className={`h-8 w-8 ${textColor}`} />
      </div>
    </div>
  </div>
));

// Uso do componente:
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
  <StatCard
    title="Pendentes"
    value={generalStats?.pending || 0}
    trend="+12% esta semana"
    icon={Clock}
    gradientFrom="from-orange-500"
    gradientTo="to-red-600"
    textColor="text-orange-100"
  />
  <StatCard
    title="Resolvidos"
    value={generalStats?.resolved || 0}
    trend="+8% esta semana"
    icon={CheckCircle}
    gradientFrom="from-green-500"
    gradientTo="to-emerald-600"
    textColor="text-green-100"
  />
</div>
```

---

## 🎯 Seção 3: Níveis (N1-N4)

### Seção Completa de Níveis:
```tsx
{/* Seção de níveis com layout em grid 2x2 */}
<div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
  {levelStats.map((level, index) => (
    <div key={level.level} className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100">
      {/* Header do nível com gradiente */}
      <div className={`bg-gradient-to-r p-4 ${
        index === 0 ? 'from-blue-600 to-blue-700' :
        index === 1 ? 'from-purple-600 to-purple-700' :
        index === 2 ? 'from-indigo-600 to-indigo-700' :
        'from-teal-600 to-teal-700'
      }`}>
        <div className="flex items-center justify-between">
          <h3 className="text-white font-bold text-lg">{level.level}</h3>
          <div className="bg-white/20 p-2 rounded-lg">
            <Users className="h-5 w-5 text-white" />
          </div>
        </div>
      </div>
      
      {/* Conteúdo do nível em grid 2x2 */}
      <div className="p-6">
        <div className="grid grid-cols-2 gap-4">
          {/* Novos */}
          <div className="text-center">
            <div className="bg-blue-50 p-3 rounded-lg mb-2">
              <Plus className="h-6 w-6 text-blue-600 mx-auto" />
            </div>
            <p className="text-2xl font-bold text-blue-600">{level.new}</p>
            <p className="text-sm text-gray-600">Novos</p>
          </div>
          
          {/* Em Progresso */}
          <div className="text-center">
            <div className="bg-yellow-50 p-3 rounded-lg mb-2">
              <Clock className="h-6 w-6 text-yellow-600 mx-auto" />
            </div>
            <p className="text-2xl font-bold text-yellow-600">{level.in_progress}</p>
            <p className="text-sm text-gray-600">Em Progr.</p>
          </div>
          
          {/* Pendentes */}
          <div className="text-center">
            <div className="bg-orange-50 p-3 rounded-lg mb-2">
              <AlertCircle className="h-6 w-6 text-orange-600 mx-auto" />
            </div>
            <p className="text-2xl font-bold text-orange-600">{level.pending}</p>
            <p className="text-sm text-gray-600">Pendentes</p>
          </div>
          
          {/* Resolvidos */}
          <div className="text-center">
            <div className="bg-green-50 p-3 rounded-lg mb-2">
              <CheckCircle className="h-6 w-6 text-green-600 mx-auto" />
            </div>
            <p className="text-2xl font-bold text-green-600">{level.resolved}</p>
            <p className="text-sm text-gray-600">Resolvidos</p>
          </div>
        </div>
      </div>
    </div>
  ))}
</div>
```

### Card de Nível Individual:
```tsx
{/* Componente de nível individual */}
const LevelCard = React.memo(({ level, index }) => {
  const gradients = [
    'from-blue-600 to-blue-700',
    'from-purple-600 to-purple-700',
    'from-indigo-600 to-indigo-700',
    'from-teal-600 to-teal-700'
  ];

  const statusItems = [
    { key: 'new', label: 'Novos', icon: Plus, bgColor: 'bg-blue-50', textColor: 'text-blue-600' },
    { key: 'in_progress', label: 'Em Progr.', icon: Clock, bgColor: 'bg-yellow-50', textColor: 'text-yellow-600' },
    { key: 'pending', label: 'Pendentes', icon: AlertCircle, bgColor: 'bg-orange-50', textColor: 'text-orange-600' },
    { key: 'resolved', label: 'Resolvidos', icon: CheckCircle, bgColor: 'bg-green-50', textColor: 'text-green-600' }
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100">
      <div className={`bg-gradient-to-r p-4 ${gradients[index]}`}>
        <div className="flex items-center justify-between">
          <h3 className="text-white font-bold text-lg">{level.level}</h3>
          <div className="bg-white/20 p-2 rounded-lg">
            <Users className="h-5 w-5 text-white" />
          </div>
        </div>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-2 gap-4">
          {statusItems.map(({ key, label, icon: Icon, bgColor, textColor }) => (
            <div key={key} className="text-center">
              <div className={`${bgColor} p-3 rounded-lg mb-2`}>
                <Icon className={`h-6 w-6 ${textColor} mx-auto`} />
              </div>
              <p className={`text-2xl font-bold ${textColor}`}>{level[key]}</p>
              <p className="text-sm text-gray-600">{label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});

// Uso:
<div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
  {levelStats.map((level, index) => (
    <LevelCard key={level.level} level={level} index={index} />
  ))}
</div>
```

---

## 👥 Seção 4: Ranking de Técnicos

### Ranking Completo:
```tsx
{/* Ranking de técnicos com posições coloridas */}
<div className="bg-white rounded-xl shadow-lg p-6 mb-8">
  <div className="flex items-center justify-between mb-6">
    <h2 className="text-2xl font-bold text-gray-800 flex items-center">
      <Trophy className="h-7 w-7 text-yellow-500 mr-3" />
      Ranking de Técnicos
    </h2>
    <div className="flex items-center space-x-2 text-sm text-gray-500">
      <Calendar className="h-4 w-4" />
      <span>Últimos 30 dias</span>
    </div>
  </div>
  
  <div className="space-y-4">
    {technicianRanking.map((tech, index) => (
      <div key={tech.name} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
        <div className="flex items-center space-x-4">
          {/* Posição com cor */}
          <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm ${
            index === 0 ? 'bg-yellow-500' :
            index === 1 ? 'bg-gray-400' :
            index === 2 ? 'bg-orange-500' : 'bg-blue-500'
          }`}>
            {index === 0 && <Crown className="h-5 w-5" />}
            {index !== 0 && (index + 1)}
          </div>
          
          {/* Avatar com iniciais */}
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
            {tech.name.split(' ').map(n => n[0]).join('')}
          </div>
          
          {/* Informações do técnico */}
          <div>
            <p className="font-semibold text-gray-800">{tech.name}</p>
            <p className="text-sm text-gray-500">Técnico de Suporte</p>
          </div>
        </div>
        
        {/* Estatísticas */}
        <div className="text-right">
          <p className="text-2xl font-bold text-gray-800">{tech.resolved_tickets}</p>
          <p className="text-sm text-gray-500">tickets resolvidos</p>
        </div>
      </div>
    ))}
  </div>
</div>
```

### Item de Ranking Individual:
```tsx
{/* Componente de item do ranking */}
const RankingItem = React.memo(({ tech, index }) => {
  const getPositionStyle = (position) => {
    const styles = {
      0: 'bg-yellow-500', // Ouro
      1: 'bg-gray-400',   // Prata
      2: 'bg-orange-500', // Bronze
    };
    return styles[position] || 'bg-blue-500';
  };

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('');
  };

  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
      <div className="flex items-center space-x-4">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm ${getPositionStyle(index)}`}>
          {index === 0 ? <Crown className="h-5 w-5" /> : (index + 1)}
        </div>
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
          {getInitials(tech.name)}
        </div>
        <div>
          <p className="font-semibold text-gray-800">{tech.name}</p>
          <p className="text-sm text-gray-500">Técnico de Suporte</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-2xl font-bold text-gray-800">{tech.resolved_tickets}</p>
        <p className="text-sm text-gray-500">tickets resolvidos</p>
      </div>
    </div>
  );
});

// Uso:
<div className="space-y-4">
  {technicianRanking.map((tech, index) => (
    <RankingItem key={tech.name} tech={tech} index={index} />
  ))}
</div>
```

---

## 🎫 Seção 5: Tickets Novos

### Seção Completa de Tickets:
```tsx
{/* Seção de tickets novos */}
<div className="bg-white rounded-xl shadow-lg p-6">
  <div className="flex items-center justify-between mb-6">
    <h2 className="text-2xl font-bold text-gray-800 flex items-center">
      <Ticket className="h-7 w-7 text-blue-500 mr-3" />
      Tickets Novos
    </h2>
    <button className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 transition-colors">
      <span className="text-sm font-medium">Ver todos</span>
      <ChevronRight className="h-4 w-4" />
    </button>
  </div>
  
  <div className="space-y-4">
    {newTickets.map((ticket) => (
      <div key={ticket.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
        {/* Header do ticket */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-3">
            <span className="text-sm font-mono text-blue-600 bg-blue-50 px-2 py-1 rounded">
              #{ticket.id}
            </span>
            <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
              Novo
            </span>
          </div>
          <span className="text-sm text-gray-500">{ticket.date}</span>
        </div>
        
        {/* Conteúdo do ticket */}
        <h3 className="font-semibold text-gray-800 mb-2">{ticket.title}</h3>
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">{ticket.description}</p>
        
        {/* Footer do ticket */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <User className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-600">{ticket.assignee || 'Não atribuído'}</span>
          </div>
          <button className="text-blue-600 hover:text-blue-800 transition-colors">
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    ))}
  </div>
</div>
```

### Card de Ticket Individual:
```tsx
{/* Componente de ticket individual */}
const TicketCard = React.memo(({ ticket }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateText = (text, maxLength = 100) => {
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-mono text-blue-600 bg-blue-50 px-2 py-1 rounded">
            #{ticket.id}
          </span>
          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
            Novo
          </span>
        </div>
        <span className="text-sm text-gray-500">{formatDate(ticket.date)}</span>
      </div>
      
      <h3 className="font-semibold text-gray-800 mb-2">{ticket.title}</h3>
      <p className="text-gray-600 text-sm mb-3">{truncateText(ticket.description)}</p>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <User className="h-4 w-4 text-gray-400" />
          <span className="text-sm text-gray-600">{ticket.assignee || 'Não atribuído'}</span>
        </div>
        <button className="text-blue-600 hover:text-blue-800 transition-colors">
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
});

// Uso:
<div className="space-y-4">
  {newTickets.map((ticket) => (
    <TicketCard key={ticket.id} ticket={ticket} />
  ))}
</div>
```

---

## 🔧 Utilitários e Helpers

### Estados de Loading:
```tsx
{/* Loading skeleton para cards */}
const LoadingSkeleton = () => (
  <div className="animate-pulse">
    <div className="bg-gray-300 h-4 rounded mb-2"></div>
    <div className="bg-gray-300 h-8 rounded mb-2"></div>
    <div className="bg-gray-300 h-3 rounded w-3/4"></div>
  </div>
);

// Uso em cards:
{loading ? (
  <div className="bg-white p-6 rounded-xl shadow-lg">
    <LoadingSkeleton />
  </div>
) : (
  // Conteúdo normal
)}
```

### Estados de Erro:
```tsx
{/* Componente de erro */}
const ErrorMessage = ({ message, onRetry }) => (
  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
    <div className="flex items-center">
      <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
      <p className="text-red-700">{message}</p>
    </div>
    {onRetry && (
      <button 
        onClick={onRetry}
        className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
      >
        Tentar novamente
      </button>
    )}
  </div>
);
```

### Hook personalizado para dados:
```tsx
{/* Hook para gerenciar dados do dashboard */}
const useDashboardData = () => {
  const [data, setData] = useState({
    generalStats: null,
    levelStats: [],
    technicianRanking: [],
    newTickets: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [general, levels, ranking, tickets] = await Promise.all([
        apiService.getGeneralStats(),
        apiService.getLevelStats(),
        apiService.getTechnicianRanking(),
        apiService.getNewTickets()
      ]);

      setData({
        generalStats: general,
        levelStats: levels,
        technicianRanking: ranking,
        newTickets: tickets
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { ...data, loading, error, refetch: fetchData };
};
```

---

## 📱 Responsividade

### Classes Tailwind para Responsividade:
```tsx
{/* Breakpoints padrão do Tailwind */}
// sm: 640px
// md: 768px
// lg: 1024px
// xl: 1280px
// 2xl: 1536px

{/* Grid responsivo para cards */}
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">

{/* Padding responsivo */}
<div className="p-4 md:p-6 lg:p-8">

{/* Texto responsivo */}
<h1 className="text-xl md:text-2xl lg:text-3xl font-bold">

{/* Espaçamento responsivo */}
<div className="space-y-4 md:space-y-6 lg:space-y-8">
```

### Container responsivo:
```tsx
{/* Container principal responsivo */}
<div className="min-h-screen bg-gray-50">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    {/* Conteúdo do dashboard */}
  </div>
</div>
```

---

## 🎨 Temas e Variações

### Tema Escuro (opcional):
```tsx
{/* Classes para tema escuro */}
<div className="dark:bg-gray-900 dark:text-white">
  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg">
    <h2 className="text-gray-800 dark:text-gray-200">Título</h2>
    <p className="text-gray-600 dark:text-gray-400">Descrição</p>
  </div>
</div>
```

### Variações de cores:
```tsx
{/* Paleta de cores alternativa */}
const colorSchemes = {
  blue: 'from-blue-500 to-blue-600',
  green: 'from-green-500 to-green-600',
  purple: 'from-purple-500 to-purple-600',
  orange: 'from-orange-500 to-orange-600',
  red: 'from-red-500 to-red-600',
  teal: 'from-teal-500 to-teal-600'
};
```

---

**Última Atualização**: $(Get-Date -Format "dd/MM/yyyy HH:mm")  
**Status**: Snippets Completos ✅