/**
 * Dashboard Page - Scout Pro
 * Página inicial com visão geral do sistema
 */
import { Users, Star, FileText, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";

export default function Dashboard() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Visão geral do sistema de scouting
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total de Jogadores"
          value="707"
          icon={Users}
          color="blue"
        />
        <StatCard
          title="Na Wishlist"
          value="42"
          icon={Star}
          color="yellow"
        />
        <StatCard
          title="Avaliações"
          value="1.2k"
          icon={FileText}
          color="green"
        />
        <StatCard
          title="Média Geral"
          value="3.8"
          icon={TrendingUp}
          color="purple"
        />
      </div>

      {/* Placeholder para futuros componentes */}
      <Card>
        <CardHeader>
          <CardTitle>Em Desenvolvimento</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600">
            Futuros componentes: gráficos de evolução, últimas avaliações,
            jogadores em destaque, etc.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string;
  value: string;
  icon: any;
  color: string;
}) {
  const colorClasses = {
    blue: "bg-blue-500",
    yellow: "bg-yellow-500",
    green: "bg-green-500",
    purple: "bg-purple-500",
  }[color];

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          </div>
          <div className={`${colorClasses} p-3 rounded-lg`}>
            <Icon className="h-6 w-6 text-white" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
