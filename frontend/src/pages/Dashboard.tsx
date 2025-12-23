/**
 * Dashboard Page - Scout Pro
 * Executive intelligence dashboard with KPIs and insights
 */
import { useQuery } from "@tanstack/react-query";
import {
  Users,
  TrendingUp,
  AlertTriangle,
  Star,
  Award,
  Activity,
  CheckCircle,
  XCircle,
  Clock,
} from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { getDashboardStats, getTopProspects, getActivityFeed, getSystemStatus } from "../api/stats";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { formatNota, getMediaColor } from "../lib/utils";

const POSITION_COLORS = [
  "#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6",
  "#EC4899", "#06B6D4", "#84CC16", "#F97316", "#6366F1",
];

export default function Dashboard() {
  // Fetch dashboard data
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: getDashboardStats,
    refetchInterval: 60000, // Refresh every minute
  });

  const { data: topProspects, isLoading: prospectsLoading } = useQuery({
    queryKey: ["top-prospects"],
    queryFn: () => getTopProspects(5),
    refetchInterval: 300000, // Refresh every 5 minutes
  });

  const { data: activityFeed, isLoading: activityLoading } = useQuery({
    queryKey: ["activity-feed"],
    queryFn: () => getActivityFeed(5),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: systemStatus } = useQuery({
    queryKey: ["system-status"],
    queryFn: getSystemStatus,
    refetchInterval: 120000, // Refresh every 2 minutes
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Visão executiva do sistema de scouting
        </p>
      </div>

      {/* System Status */}
      {systemStatus && (
        <SystemStatusBar status={systemStatus} />
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total de Jogadores"
          value={stats?.total_jogadores || 0}
          growth={stats?.crescimento_semanal}
          icon={Users}
          color="blue"
          isLoading={statsLoading}
        />
        <KPICard
          title="Média Geral da Base"
          value={formatNota(stats?.media_geral || 0)}
          subtitle={`Meta: ${formatNota(stats?.meta_clube || 0)}`}
          icon={TrendingUp}
          color="green"
          isLoading={statsLoading}
          alert={stats && stats.media_geral < stats.meta_clube}
        />
        <KPICard
          title="Alertas de Contrato"
          value={stats?.alertas_contrato || 0}
          subtitle="Vencendo em < 12 meses"
          icon={AlertTriangle}
          color="yellow"
          isLoading={statsLoading}
          alert={stats && stats.alertas_contrato > 0}
        />
        <KPICard
          title="Wishlist Ativa"
          value={stats?.wishlist_ativa || 0}
          subtitle="Jogadores monitorados"
          icon={Star}
          color="purple"
          isLoading={statsLoading}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Prospects */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Award className="h-5 w-5 text-yellow-600" />
                <CardTitle>Top Prospects (Sub-23)</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              {prospectsLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse flex gap-3">
                      <div className="h-16 w-16 bg-gray-200 rounded-full" />
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-gray-200 rounded w-3/4" />
                        <div className="h-3 bg-gray-200 rounded w-1/2" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {topProspects?.map((player, index) => (
                    <div
                      key={player.id_jogador}
                      className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-yellow-100 text-yellow-700 font-bold">
                        {index + 1}
                      </div>
                      <img
                        src={
                          player.transfermarkt_id
                            ? `https://img.a.transfermarkt.technology/portrait/header/${player.transfermarkt_id}.jpg`
                            : "/placeholder-player.png"
                        }
                        alt={player.nome}
                        className="h-16 w-16 rounded-full object-cover border-2 border-yellow-500"
                        onError={(e) => {
                          e.currentTarget.src = "/placeholder-player.png";
                        }}
                      />
                      <div className="flex-1">
                        <div className="font-semibold text-gray-900">
                          {player.nome}
                        </div>
                        <div className="text-sm text-gray-600">
                          {player.idade_atual} anos • {player.posicao} •{" "}
                          {player.clube}
                        </div>
                      </div>
                      <div className="text-right">
                        <div
                          className={`text-2xl font-bold ${getMediaColor(
                            player.media_geral
                          )}`}
                        >
                          {formatNota(player.media_geral)}
                        </div>
                        <div className="text-xs text-gray-500">Média Geral</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Distribution by Position (Pie Chart) */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Distribuição por Posição</CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <div className="h-64 flex items-center justify-center">
                  <div className="text-gray-400">Carregando...</div>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={stats?.distribuicao_posicao || []}
                      dataKey="count"
                      nameKey="posicao"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label={(entry) => `${entry.posicao} (${entry.count})`}
                      labelLine={false}
                    >
                      {stats?.distribuicao_posicao.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={POSITION_COLORS[index % POSITION_COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Activity Feed */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-blue-600" />
            <CardTitle>Feed de Atividade</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {activityLoading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse flex gap-3">
                  <div className="h-10 w-10 bg-gray-200 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {activityFeed?.map((item) => (
                <ActivityItem key={item.id} item={item} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * KPI Card Component
 */
function KPICard({
  title,
  value,
  subtitle,
  growth,
  icon: Icon,
  color,
  isLoading,
  alert,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  growth?: number;
  icon: any;
  color: string;
  isLoading?: boolean;
  alert?: boolean;
}) {
  const colorClasses: Record<string, string> = {
    blue: "bg-blue-500",
    green: "bg-green-500",
    yellow: "bg-yellow-500",
    purple: "bg-purple-500",
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="animate-pulse space-y-3">
            <div className="h-4 bg-gray-200 rounded w-1/2" />
            <div className="h-8 bg-gray-200 rounded w-3/4" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={alert ? "border-yellow-500 border-2" : ""}>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
            {subtitle && (
              <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
            )}
            {growth !== undefined && (
              <div
                className={`text-sm mt-2 flex items-center gap-1 ${
                  growth >= 0 ? "text-green-600" : "text-red-600"
                }`}
              >
                <TrendingUp className="h-3 w-3" />
                {growth >= 0 ? "+" : ""}
                {growth}% esta semana
              </div>
            )}
          </div>
          <div className={`${colorClasses[color]} p-3 rounded-lg`}>
            <Icon className="h-6 w-6 text-white" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Activity Item Component
 */
function ActivityItem({ item }: { item: any }) {
  const iconMap = {
    avaliacao: FileText,
    jogador_novo: Users,
    wishlist_add: Star,
  };

  const colorMap = {
    avaliacao: "bg-blue-100 text-blue-600",
    jogador_novo: "bg-green-100 text-green-600",
    wishlist_add: "bg-purple-100 text-purple-600",
  };

  const Icon = iconMap[item.tipo as keyof typeof iconMap] || Activity;
  const colorClass = colorMap[item.tipo as keyof typeof colorMap] || "bg-gray-100 text-gray-600";

  const timeAgo = getTimeAgo(new Date(item.created_at));

  return (
    <div className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
      <div className={`p-2 rounded-full ${colorClass}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1">
        <p className="text-sm text-gray-900">{item.descricao}</p>
        <p className="text-xs text-gray-500 mt-1">
          {item.usuario} • {timeAgo}
        </p>
      </div>
    </div>
  );
}

/**
 * System Status Bar Component
 */
function SystemStatusBar({ status }: { status: any }) {
  const getStatusIcon = (state: string) => {
    if (state === "online") return <CheckCircle className="h-4 w-4 text-green-600" />;
    if (state === "offline") return <XCircle className="h-4 w-4 text-red-600" />;
    return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
  };

  const getStatusColor = (state: string) => {
    if (state === "online") return "bg-green-50 border-green-200";
    if (state === "offline") return "bg-red-50 border-red-200";
    return "bg-yellow-50 border-yellow-200";
  };

  const allOnline =
    status.api_transfermarkt === "online" &&
    status.google_sheets === "online" &&
    status.database === "online";

  return (
    <div
      className={`border rounded-lg p-4 ${
        allOnline ? "bg-green-50 border-green-200" : "bg-yellow-50 border-yellow-200"
      }`}
    >
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            {getStatusIcon(status.database)}
            <span className="text-sm font-medium text-gray-700">Database</span>
          </div>
          <div className="flex items-center gap-2">
            {getStatusIcon(status.api_transfermarkt)}
            <span className="text-sm font-medium text-gray-700">Transfermarkt</span>
          </div>
          <div className="flex items-center gap-2">
            {getStatusIcon(status.google_sheets)}
            <span className="text-sm font-medium text-gray-700">Google Sheets</span>
          </div>
        </div>
        {status.ultimo_sync && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="h-4 w-4" />
            Último sync: {getTimeAgo(new Date(status.ultimo_sync))}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Time ago helper
 */
function getTimeAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "agora";
  if (diffMins < 60) return `${diffMins}min atrás`;
  if (diffHours < 24) return `${diffHours}h atrás`;
  return `${diffDays}d atrás`;
}
