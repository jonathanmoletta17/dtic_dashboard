import { useState, useEffect } from 'react';
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
  Ticket,
  LoaderCircle,
  ServerCrash
} from "lucide-react";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Badge } from "./components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { fetchGeneralStats, fetchLevelStats, fetchTechnicianRanking, fetchNewTickets } from './services/api';
import type { GeneralStats, LevelStats, TechnicianRankingItem, NewTicketItem } from './types/api.d';

export default function App() {
  const [generalStats, setGeneralStats] = useState<GeneralStats | null>(null);
  const [levelStats, setLevelStats] = useState<LevelStats | null>(null);
  const [ranking, setRanking] = useState<TechnicianRankingItem[] | null>(null);
  const [newTickets, setNewTickets] = useState<NewTicketItem[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [generalStatsData, levelStatsData, rankingData, newTicketsData] = await Promise.all([
        fetchGeneralStats(),
        fetchLevelStats(),
        fetchTechnicianRanking(),
        fetchNewTickets(),
      ]);
      setGeneralStats(generalStatsData);
      setLevelStats(levelStatsData);
      setRanking(rankingData);
      setNewTickets(newTicketsData);
    } catch (err: any) {
      console.error("Falha ao buscar dados do dashboard:", err);
      setError(err.message || 'Ocorreu um erro desconhecido.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 flex flex-col">
      <header className="bg-[#5A9BD4] text-white p-4 flex items-center justify-between shadow-md flex-shrink-0">
        {/* Header content... (simplificado para brevidade) */}
        <div className="flex items-center gap-6">
          <h1 className="text-xl font-semibold">Dashboard GLPI</h1>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" className="text-white hover:bg-blue-600" onClick={loadDashboardData} disabled={isLoading}>
            <RotateCcw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </header>

      <main className="p-6 bg-gray-100 flex-1 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-full text-gray-500"><LoaderCircle className="w-8 h-8 animate-spin mr-4" /><span>Carregando...</span></div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full text-red-600"><ServerCrash className="w-12 h-12 mb-4" /><h2 className="text-xl font-semibold">Falha ao Carregar</h2><p>{error}</p><Button onClick={loadDashboardData} className="mt-6">Tentar Novamente</Button></div>
        ) : (
          <div className="flex gap-6 h-full">
            <div className="flex-1 flex flex-col gap-4">
              {/* General Stats */}
              <div className="grid grid-cols-4 gap-4">
                <Card><CardContent className="p-4"><div><p className="text-sm text-gray-600">Novos</p><p className="text-2xl font-semibold">{generalStats?.novos ?? 0}</p></div></CardContent></Card>
                <Card><CardContent className="p-4"><div><p className="text-sm text-gray-600">Em Progresso</p><p className="text-2xl font-semibold">{generalStats?.em_progresso ?? 0}</p></div></CardContent></Card>
                <Card><CardContent className="p-4"><div><p className="text-sm text-gray-600">Pendentes</p><p className="text-2xl font-semibold">{generalStats?.pendentes ?? 0}</p></div></CardContent></Card>
                <Card><CardContent className="p-4"><div><p className="text-sm text-gray-600">Resolvidos</p><p className="text-2xl font-semibold">{generalStats?.resolvidos ?? 0}</p></div></CardContent></Card>
              </div>

              {/* Level Stats (Grid 2x2) */}
              <div className="grid grid-cols-2 gap-4">
                {levelStats && (Object.keys(levelStats) as Array<keyof typeof levelStats>).map(level => {
                  const details = levelStats[level];
                  return (
                    <Card key={level} className="bg-white shadow-sm">
                      <CardHeader className="pb-2"><CardTitle className="flex items-center justify-between"><span className="flex items-center gap-2 text-sm"><Activity className="w-4 h-4" />Nível {level}</span><span className="text-xl font-semibold">{details.total}</span></CardTitle></CardHeader>
                      <CardContent className="pt-0"><div className="grid grid-cols-2 gap-2 text-sm">
                        <div><span className="text-gray-600">Novos:</span><span className="font-medium float-right">{details.novos}</span></div>
                        <div><span className="text-gray-600">Em Progr.:</span><span className="font-medium float-right">{details.em_progresso}</span></div>
                        <div><span className="text-gray-600">Pendentes:</span><span className="font-medium float-right">{details.pendentes}</span></div>
                        <div><span className="text-gray-600">Resolvidos:</span><span className="font-medium float-right">{details.resolvidos}</span></div>
                      </div></CardContent>
                    </Card>
                  );
                })}
              </div>

              {/* Ranking de Técnicos (no rodapé) */}
              <div className="mt-auto">
                <Card className="bg-white shadow-sm">
                  <CardHeader className="pb-2"><CardTitle className="flex items-center gap-2 text-lg"><Award className="w-5 h-5" />Ranking de Técnicos</CardTitle></CardHeader>
                  <CardContent><div className="grid grid-cols-4 gap-3">
                    {ranking?.map((tech, index) => (
                      <div key={tech.tecnico} className="text-center p-3 rounded-lg bg-slate-700 text-white">
                        <Badge>#{index + 1}</Badge>
                        <p className="font-medium truncate mt-1" title={tech.tecnico}>{tech.tecnico}</p>
                        <p className="text-sm">{tech.tickets} tickets</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Column - Tickets */}
            <div className="w-80 flex flex-col">
              <Card className="bg-white shadow-sm h-full flex flex-col">
                <CardHeader><CardTitle>Tickets Novos</CardTitle></CardHeader>
                <CardContent className="flex-1 overflow-y-auto space-y-3">
                  {newTickets?.map(ticket => (
                    <div key={ticket.id} className="p-3 rounded-lg border">
                      <div className="flex justify-between text-xs mb-1"><span className="font-mono">#{ticket.id}</span><span>{ticket.data}</span></div>
                      <p className="font-medium truncate" title={ticket.titulo}>{ticket.titulo}</p>
                      <p className="text-sm text-gray-600 truncate">{ticket.solicitante}</p>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
          </div>
        )}
      </main>
    </div>
  );
}