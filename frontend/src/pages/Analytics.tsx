/**
 * Analytics Page - Scout Pro
 * Scatter plot visualization with configurable axes and filters
 */
import { useState, useMemo } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis,
} from "recharts";
import { TrendingUp, Filter } from "lucide-react";
import { useJogadores } from "../hooks/useJogadores";
import { calcularMedia } from "../lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { POSICOES } from "../types";

type AxisType = "idade" | "media_geral" | "valor_mercado";

export default function Analytics() {
  const [xAxis, setXAxis] = useState<AxisType>("idade");
  const [yAxis, setYAxis] = useState<AxisType>("media_geral");
  const [selectedPosition, setSelectedPosition] = useState<string | null>(null);
  const [ageRange, setAgeRange] = useState<[number, number]>([16, 35]);

  // Fetch all players
  const { data: jogadoresData, isLoading } = useJogadores({ limit: 1000 });

  // Process data for scatter plot
  const scatterData = useMemo(() => {
    if (!jogadoresData?.data) return [];

    return jogadoresData.data
      .filter((jogador) => {
        // Filter by position
        if (selectedPosition && jogador.posicao !== selectedPosition) {
          return false;
        }

        // Filter by age range
        if (
          jogador.idade_atual &&
          (jogador.idade_atual < ageRange[0] || jogador.idade_atual > ageRange[1])
        ) {
          return false;
        }

        return true;
      })
      .map((jogador) => {
        const media = calcularMedia([jogador.nota_potencial_media]);

        return {
          id: jogador.id_jogador,
          nome: jogador.nome,
          posicao: jogador.posicao,
          clube: jogador.clube,
          idade: jogador.idade_atual || 0,
          media_geral: media || 0,
          valor_mercado: jogador.valor_mercado_euros
            ? jogador.valor_mercado_euros / 1_000_000
            : 0,
          foto: jogador.transfermarkt_id
            ? `https://img.a.transfermarkt.technology/portrait/header/${jogador.transfermarkt_id}.jpg`
            : null,
        };
      })
      .filter((item) => item[xAxis] > 0 && item[yAxis] > 0); // Remove invalid data
  }, [jogadoresData, selectedPosition, ageRange, xAxis, yAxis]);

  // Axis labels
  const axisLabels: Record<AxisType, string> = {
    idade: "Idade",
    media_geral: "Média Geral",
    valor_mercado: "Valor de Mercado (€M)",
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="bg-purple-100 p-2 rounded-lg">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <CardTitle className="text-2xl">Analytics</CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                Análise de dispersão com eixos configuráveis
              </p>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-gray-600" />
            <CardTitle className="text-lg">Filtros</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* X Axis Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Eixo X
              </label>
              <select
                value={xAxis}
                onChange={(e) => setXAxis(e.target.value as AxisType)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="idade">Idade</option>
                <option value="media_geral">Média Geral</option>
                <option value="valor_mercado">Valor de Mercado</option>
              </select>
            </div>

            {/* Y Axis Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Eixo Y
              </label>
              <select
                value={yAxis}
                onChange={(e) => setYAxis(e.target.value as AxisType)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="idade">Idade</option>
                <option value="media_geral">Média Geral</option>
                <option value="valor_mercado">Valor de Mercado</option>
              </select>
            </div>

            {/* Position Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Posição
              </label>
              <select
                value={selectedPosition || ""}
                onChange={(e) =>
                  setSelectedPosition(e.target.value || null)
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todas</option>
                {POSICOES.map((pos) => (
                  <option key={pos} value={pos}>
                    {pos}
                  </option>
                ))}
              </select>
            </div>

            {/* Clear Filters */}
            <div className="flex items-end">
              <Button
                variant="outline"
                onClick={() => {
                  setSelectedPosition(null);
                  setAgeRange([16, 35]);
                }}
                className="w-full"
              >
                Limpar Filtros
              </Button>
            </div>
          </div>

          {/* Age Range Slider */}
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Faixa Etária: {ageRange[0]} - {ageRange[1]} anos
            </label>
            <div className="flex gap-4">
              <input
                type="range"
                min="16"
                max="35"
                value={ageRange[0]}
                onChange={(e) =>
                  setAgeRange([parseInt(e.target.value), ageRange[1]])
                }
                className="flex-1"
              />
              <input
                type="range"
                min="16"
                max="35"
                value={ageRange[1]}
                onChange={(e) =>
                  setAgeRange([ageRange[0], parseInt(e.target.value)])
                }
                className="flex-1"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Scatter Plot */}
      <Card>
        <CardHeader>
          <CardTitle>
            {axisLabels[yAxis]} vs {axisLabels[xAxis]}
          </CardTitle>
          <p className="text-sm text-gray-600 mt-1">
            {scatterData.length} jogadores exibidos
          </p>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="h-96 flex items-center justify-center">
              <div className="text-gray-500">Carregando dados...</div>
            </div>
          ) : scatterData.length === 0 ? (
            <div className="h-96 flex items-center justify-center">
              <div className="text-center">
                <p className="text-gray-500 mb-2">
                  Nenhum jogador encontrado com os filtros selecionados
                </p>
                <Button
                  variant="outline"
                  onClick={() => {
                    setSelectedPosition(null);
                    setAgeRange([16, 35]);
                  }}
                >
                  Limpar Filtros
                </Button>
              </div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={500}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis
                  type="number"
                  dataKey={xAxis}
                  name={axisLabels[xAxis]}
                  stroke="#6B7280"
                  label={{
                    value: axisLabels[xAxis],
                    position: "insideBottom",
                    offset: -10,
                  }}
                />
                <YAxis
                  type="number"
                  dataKey={yAxis}
                  name={axisLabels[yAxis]}
                  stroke="#6B7280"
                  label={{
                    value: axisLabels[yAxis],
                    angle: -90,
                    position: "insideLeft",
                  }}
                />
                <ZAxis range={[100, 400]} />
                <Tooltip content={<CustomTooltip />} />
                <Scatter
                  data={scatterData}
                  fill="#3B82F6"
                  fillOpacity={0.6}
                />
              </ScatterChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* Stats Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Resumo Estatístico</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              label="Total de Jogadores"
              value={scatterData.length}
              color="blue"
            />
            <StatCard
              label="Idade Média"
              value={
                scatterData.length > 0
                  ? (
                      scatterData.reduce((sum, p) => sum + p.idade, 0) /
                      scatterData.length
                    ).toFixed(1)
                  : "0"
              }
              color="green"
            />
            <StatCard
              label="Média Geral"
              value={
                scatterData.length > 0
                  ? (
                      scatterData.reduce((sum, p) => sum + p.media_geral, 0) /
                      scatterData.length
                    ).toFixed(2)
                  : "0"
              }
              color="purple"
            />
            <StatCard
              label="Valor Médio"
              value={
                scatterData.length > 0
                  ? `€${(
                      scatterData.reduce((sum, p) => sum + p.valor_mercado, 0) /
                      scatterData.length
                    ).toFixed(1)}M`
                  : "€0M"
              }
              color="yellow"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Custom Tooltip with player photo and info
 */
function CustomTooltip({ active, payload }: any) {
  if (!active || !payload || payload.length === 0) return null;

  const data = payload[0].payload;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 max-w-xs">
      <div className="flex items-start gap-3">
        {/* Player Photo */}
        {data.foto && (
          <img
            src={data.foto}
            alt={data.nome}
            className="h-16 w-16 rounded-full object-cover border-2 border-blue-500"
            onError={(e) => {
              e.currentTarget.style.display = "none";
            }}
          />
        )}

        {/* Player Info */}
        <div className="flex-1">
          <div className="font-semibold text-gray-900 mb-1">{data.nome}</div>
          <div className="text-xs text-gray-600 space-y-1">
            <div>
              <span className="font-medium">Posição:</span> {data.posicao || "N/A"}
            </div>
            <div>
              <span className="font-medium">Clube:</span> {data.clube || "Sem clube"}
            </div>
            <div>
              <span className="font-medium">Idade:</span> {data.idade} anos
            </div>
            <div>
              <span className="font-medium">Média:</span> {data.media_geral.toFixed(2)}
            </div>
            {data.valor_mercado > 0 && (
              <div>
                <span className="font-medium">Valor:</span> €{data.valor_mercado.toFixed(1)}M
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Stat Card Component
 */
function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string | number;
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: "bg-blue-500",
    green: "bg-green-500",
    purple: "bg-purple-500",
    yellow: "bg-yellow-500",
  };

  return (
    <div className="text-center">
      <div className={`inline-block ${colorClasses[color]} p-3 rounded-lg mb-2`}>
        <div className="text-2xl font-bold text-white">{value}</div>
      </div>
      <div className="text-sm text-gray-600">{label}</div>
    </div>
  );
}
