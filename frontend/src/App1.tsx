import { 
  useState, 
  useEffect 
} from 'react';
import { 
  Bell, 
  ChevronLeft, 
  RotateCcw, 
  Search, 
  Settings, 
  User, 
  TrendingUp,
  AlertTriangle,
  Clock,
  CheckCircle,
  Activity,
  Award,
  Ticket
} from "lucide-react";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Badge } from "./components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { fetchNewTickets, fetchGeneralStats } from './services/api';
import type { NewTicketItem, GeneralStats } from './types/api.d';

export default function App1() {
  const [newTickets, setNewTickets] = useState<NewTicketItem[] | null>(null);
  const [generalStats, setGeneralStats] = useState<GeneralStats | null>(null);

  const loadDashboardData = async () => {
    // Carrega Tickets Novos de forma independente
    try {
      const newTicketsData = await fetchNewTickets();
      setNewTickets(newTicketsData);
    } catch (err) {
      console.error('Falha ao buscar Tickets Novos (App1):', err);
    }

    // Carrega Métricas Gerais (não impacta Tickets Novos em caso de erro)
    try {
      const gs = await fetchGeneralStats();
      setGeneralStats(gs);
    } catch (err) {
      console.error('Falha ao buscar Métricas Gerais (App1):', err);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-[#5A9BD4] text-white p-4 flex items-center justify-between shadow-md">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" className="text-white hover:bg-blue-600">
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <div>
            <h1 className="text-xl font-semibold">Dashboard GLPI</h1>
            <p className="text-sm text-blue-100">Departamento de Tecnologia do Estado</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-white/20 rounded-lg px-4 py-2 w-80">
            <Search className="w-4 h-4 text-white/80" />
            <Input 
              placeholder="Buscar chamados... (Ctrl+K)" 
              className="bg-transparent border-none text-white placeholder:text-white/70 flex-1"
            />
          </div>
          <Button variant="ghost" size="sm" className="text-white hover:bg-blue-600">
            <RotateCcw className="w-4 h-4" />
          </Button>
          <Button variant="ghost" size="sm" className="text-white hover:bg-blue-600 relative">
            <Bell className="w-4 h-4" />
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </Button>
          <Button variant="ghost" size="sm" className="text-white hover:bg-blue-600">
            <Settings className="w-4 h-4" />
          </Button>
          <div className="flex items-center gap-3 ml-4 pl-4 border-l border-white/20">
            <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <div className="text-sm">
              <p className="text-white font-medium">Admin</p>
              <p className="text-blue-100 text-xs">17:38:57</p>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="p-6 bg-gray-100 h-[calc(100vh-80px)] overflow-hidden">
        <div className="flex gap-4 h-full">
          {/* Left Column - Dashboard Stats */}
          <div className="flex-1 flex flex-col">
            {/* Stats Cards */}
            <div className="grid grid-cols-4 gap-4 mb-4">
              <Card className="bg-white border-l-4 border-l-[#5A9BD4] shadow-sm hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Novos</p>
                      <p className="text-2xl font-semibold text-gray-900">{new Intl.NumberFormat('pt-BR').format(generalStats?.novos ?? 3)}</p>
                    </div>
                    <div className="w-10 h-10 bg-[#5A9BD4]/10 rounded-lg flex items-center justify-center">
                      <TrendingUp className="w-5 h-5 text-[#5A9BD4]" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white border-l-4 border-l-orange-500 shadow-sm hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Em Progresso</p>
                      <p className="text-2xl font-semibold text-gray-900">{new Intl.NumberFormat('pt-BR').format(generalStats?.em_progresso ?? 45)}</p>
                    </div>
                    <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                      <AlertTriangle className="w-5 h-5 text-orange-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white border-l-4 border-l-amber-500 shadow-sm hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Pendentes</p>
                      <p className="text-2xl font-semibold text-gray-900">{new Intl.NumberFormat('pt-BR').format(generalStats?.pendentes ?? 26)}</p>
                    </div>
                    <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                      <Clock className="w-5 h-5 text-amber-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white border-l-4 border-l-green-500 shadow-sm hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Resolvidos</p>
                      <p className="text-2xl font-semibold text-gray-900">{new Intl.NumberFormat('pt-BR').format(generalStats?.resolvidos ?? 10200)}</p>
                    </div>
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Level Stats - 2x2 Grid */}
            <div className="grid grid-cols-2 gap-4 mb-4">
              {/* Nível N1 */}
              <Card className="bg-white shadow-sm border-0">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-[#5A9BD4] text-sm">
                      <Activity className="w-4 h-4" />
                      Nível N1
                    </span>
                    <span className="text-xl font-semibold text-gray-900">1.495</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-[#5A9BD4] rounded-full"></span>
                        Novos
                      </span>
                      <span className="font-medium text-gray-900 text-sm">1</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        Em Progr.
                      </span>
                      <span className="font-medium text-gray-900 text-sm">8</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-amber-500 rounded-full"></span>
                        Pendentes
                      </span>
                      <span className="font-medium text-gray-900 text-sm">3</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        Resolvidos
                      </span>
                      <span className="font-medium text-gray-900 text-sm">1.483</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Nível N2 */}
              <Card className="bg-white shadow-sm border-0">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-[#5A9BD4] text-sm">
                      <Activity className="w-4 h-4" />
                      Nível N2
                    </span>
                    <span className="text-xl font-semibold text-gray-900">1.266</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-[#5A9BD4] rounded-full"></span>
                        Novos
                      </span>
                      <span className="font-medium text-gray-900 text-sm">0</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        Em Progr.
                      </span>
                      <span className="font-medium text-gray-900 text-sm">11</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-amber-500 rounded-full"></span>
                        Pendentes
                      </span>
                      <span className="font-medium text-gray-900 text-sm">11</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        Resolvidos
                      </span>
                      <span className="font-medium text-gray-900 text-sm">1.244</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Nível N3 */}
              <Card className="bg-white shadow-sm border-0">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-[#5A9BD4] text-sm">
                      <Activity className="w-4 h-4" />
                      Nível N3
                    </span>
                    <span className="text-xl font-semibold text-gray-900">5.262</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-[#5A9BD4] rounded-full"></span>
                        Novos
                      </span>
                      <span className="font-medium text-gray-900 text-sm">1</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        Em Progr.
                      </span>
                      <span className="font-medium text-gray-900 text-sm">21</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-amber-500 rounded-full"></span>
                        Pendentes
                      </span>
                      <span className="font-medium text-gray-900 text-sm">9</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        Resolvidos
                      </span>
                      <span className="font-medium text-gray-900 text-sm">5.231</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Nível N4 */}
              <Card className="bg-white shadow-sm border-0">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-[#5A9BD4] text-sm">
                      <Activity className="w-4 h-4" />
                      Nível N4
                    </span>
                    <span className="text-xl font-semibold text-gray-900">42</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-[#5A9BD4] rounded-full"></span>
                        Novos
                      </span>
                      <span className="font-medium text-gray-900 text-sm">0</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        Em Progr.
                      </span>
                      <span className="font-medium text-gray-900 text-sm">1</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-amber-500 rounded-full"></span>
                        Pendentes
                      </span>
                      <span className="font-medium text-gray-900 text-sm">1</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        Resolvidos
                      </span>
                      <span className="font-medium text-gray-900 text-sm">40</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Ranking de Técnicos */}
            <Card className="bg-white shadow-sm border-0 flex-1">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-[#5A9BD4] text-lg">
                  <Award className="w-5 h-5" />
                  Ranking de Técnicos
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-3">
                  <div className="bg-gradient-to-br from-[#5A9BD4] to-[#4A8BC2] text-white p-3 rounded-lg shadow-sm">
                    <div className="text-center">
                      <Badge className="bg-yellow-500 text-yellow-900 mb-2 font-medium text-xs">#1</Badge>
                      <p className="text-xs font-medium mb-1">Roberlâncio O.</p>
                      <p className="text-xs text-blue-100 mb-2">Arquitetos da Silva V.</p>
                      <div className="space-y-1">
                        <div className="text-xs">
                          <span className="text-blue-100">Total:</span>
                          <span className="font-medium ml-1">2.723</span>
                        </div>
                        <div className="text-xs">
                          <span className="text-blue-100">Resolvidos:</span>
                          <span className="font-medium ml-1">2.710</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-slate-600 to-slate-700 text-white p-3 rounded-lg shadow-sm">
                    <div className="text-center">
                      <Badge className="bg-gray-300 text-gray-800 mb-2 font-medium text-xs">#2</Badge>
                      <p className="text-xs font-medium mb-1">Silvia M.</p>
                      <p className="text-xs text-slate-200 mb-2">Silvia Glediano Vale</p>
                      <div className="space-y-1">
                        <div className="text-xs">
                          <span className="text-slate-200">Total:</span>
                          <span className="font-medium ml-1">1.827</span>
                        </div>
                        <div className="text-xs">
                          <span className="text-slate-200">Resolvidos:</span>
                          <span className="font-medium ml-1">1.819</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-orange-600 to-orange-700 text-white p-3 rounded-lg shadow-sm">
                    <div className="text-center">
                      <Badge className="bg-orange-200 text-orange-900 mb-2 font-medium text-xs">#3</Badge>
                      <p className="text-xs font-medium mb-1">Jorge J.</p>
                      <p className="text-xs text-orange-100 mb-2">Jorge Antônio Vicente Jr.</p>
                      <div className="space-y-1">
                        <div className="text-xs">
                          <span className="text-orange-100">Total:</span>
                          <span className="font-medium ml-1">1.792</span>
                        </div>
                        <div className="text-xs">
                          <span className="text-orange-100">Resolvidos:</span>
                          <span className="font-medium ml-1">1.757</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-[#5A9BD4] to-[#4A8BC2] text-white p-3 rounded-lg shadow-sm">
                    <div className="text-center">
                      <Badge className="bg-blue-200 text-blue-900 mb-2 font-medium text-xs">#4</Badge>
                      <p className="text-xs font-medium mb-1">Pablo G.</p>
                      <p className="text-xs text-blue-100 mb-2">Pablo Hetking Guimarães</p>
                      <div className="space-y-1">
                        <div className="text-xs">
                          <span className="text-blue-100">Total:</span>
                          <span className="font-medium ml-1">1.338</span>
                        </div>
                        <div className="text-xs">
                          <span className="text-blue-100">Resolvidos:</span>
                          <span className="font-medium ml-1">1.329</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Tickets */}
          <div className="w-110">
            <Card className="bg-white shadow-sm border-0 h-full flex flex-col">
              <CardHeader className="pb-3 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 text-[#5A9BD4] text-lg">
                    <Ticket className="w-5 h-5" />
                    Tickets Novos
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded-md">{newTickets ? `${newTickets.length} tickets` : '0 tickets'}</span>
                    <Button variant="ghost" size="sm" className="text-gray-500 hover:text-gray-700 hover:bg-gray-100" onClick={loadDashboardData}>
                      <RotateCcw className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex-1 overflow-hidden p-0">
                <div 
                  className="h-full overflow-y-auto px-6 pb-6 [&::-webkit-scrollbar]:w-[6px] [&::-webkit-scrollbar-track]:bg-slate-100 [&::-webkit-scrollbar-track]:rounded-sm [&::-webkit-scrollbar-thumb]:bg-[#5A9BD4] [&::-webkit-scrollbar-thumb]:rounded-sm [&::-webkit-scrollbar-thumb:hover]:bg-[#4A8BC2]" 
                  style={{
                    scrollbarWidth: 'thin',
                    scrollbarColor: '#5A9BD4 #f1f5f9'
                  }}
                >
                  <div className="space-y-3">
                    {(newTickets ?? []).map((ticket) => (
                      <div key={`${ticket.id}-${ticket.data}-${ticket.titulo}`} className="border-l-4 border-[#5A9BD4] bg-[#5A9BD4]/5 p-3 rounded-r-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-mono text-gray-500 bg-gray-100 px-2 py-1 rounded">#{ticket.id ?? '-'}</span>
                          <Badge variant="outline" className="border-[#5A9BD4] text-[#5A9BD4] bg-[#5A9BD4]/10 text-xs">Novo</Badge>
                        </div>
                        <h4 className="font-medium text-gray-900 mb-2 text-sm">{ticket.titulo}</h4>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-700 font-medium">{ticket.solicitante}</span>
                          <span className="text-gray-500">{ticket.data}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
