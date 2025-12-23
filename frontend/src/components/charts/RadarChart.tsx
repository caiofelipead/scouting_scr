/**
 * RadarChart Component - Scout Pro
 * Visualização de métricas de jogadores em gráfico radar
 * Suporta comparação de até 2 jogadores simultaneamente
 */
import {
  Radar,
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import { cn } from "../../lib/utils";

export interface PlayerMetrics {
  potencial: number | null;
  tatico: number | null;
  tecnico: number | null;
  fisico: number | null;
  mental: number | null;
}

export interface RadarChartData {
  name: string; // Nome do jogador
  metrics: PlayerMetrics;
  color?: string; // Cor personalizada
}

interface RadarChartProps {
  /** Dados do jogador principal */
  player1: RadarChartData;
  /** Dados do jogador de comparação (opcional) */
  player2?: RadarChartData;
  /** Altura do gráfico em pixels */
  height?: number;
  /** Classe CSS adicional */
  className?: string;
}

/**
 * Normaliza métricas de 0-5 para 0-100
 */
function normalizeMetrics(metrics: PlayerMetrics) {
  return {
    Potencial: metrics.potencial ? (metrics.potencial / 5) * 100 : 0,
    Tático: metrics.tatico ? (metrics.tatico / 5) * 100 : 0,
    Técnico: metrics.tecnico ? (metrics.tecnico / 5) * 100 : 0,
    Físico: metrics.fisico ? (metrics.fisico / 5) * 100 : 0,
    Mental: metrics.mental ? (metrics.mental / 5) * 100 : 0,
  };
}

/**
 * Converte métricas normalizadas de volta para escala 0-5
 */
function denormalizeValue(value: number): string {
  return ((value / 100) * 5).toFixed(1);
}

/**
 * Tooltip customizado para exibir valores exatos
 */
function CustomTooltip({ active, payload }: any) {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
      <p className="font-semibold text-sm mb-2 text-gray-700">
        {payload[0]?.payload?.metric}
      </p>
      {payload.map((entry: any, index: number) => (
        <div key={index} className="flex items-center gap-2 text-sm">
          <div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-gray-600">{entry.name}:</span>
          <span className="font-semibold text-gray-900">
            {denormalizeValue(entry.value)} / 5.0
          </span>
        </div>
      ))}
    </div>
  );
}

/**
 * RadarChart - Visualização de 5 dimensões do jogador
 *
 * @example
 * // Jogador único
 * <RadarChart
 *   player1={{
 *     name: "Neymar",
 *     metrics: { potencial: 4.5, tatico: 4.2, tecnico: 4.8, fisico: 3.9, mental: 4.1 }
 *   }}
 * />
 *
 * @example
 * // Comparação de 2 jogadores
 * <RadarChart
 *   player1={{
 *     name: "Neymar",
 *     metrics: { potencial: 4.5, tatico: 4.2, tecnico: 4.8, fisico: 3.9, mental: 4.1 },
 *     color: "#3B82F6"
 *   }}
 *   player2={{
 *     name: "Vinicius Jr",
 *     metrics: { potencial: 4.7, tatico: 3.8, tecnico: 4.5, fisico: 4.6, mental: 3.9 },
 *     color: "#FBBF24"
 *   }}
 * />
 */
export default function RadarChart({
  player1,
  player2,
  height = 400,
  className,
}: RadarChartProps) {
  // Normaliza métricas para 0-100
  const normalized1 = normalizeMetrics(player1.metrics);
  const normalized2 = player2 ? normalizeMetrics(player2.metrics) : null;

  // Cores padrão (Azul e Amarelo do projeto original)
  const color1 = player1.color || "#3B82F6"; // Blue-500
  const color2 = player2?.color || "#FBBF24"; // Yellow-400

  // Prepara dados para o Recharts
  const chartData = [
    {
      metric: "Potencial",
      [player1.name]: normalized1.Potencial,
      ...(normalized2 && { [player2.name]: normalized2.Potencial }),
    },
    {
      metric: "Tático",
      [player1.name]: normalized1.Tático,
      ...(normalized2 && { [player2.name]: normalized2.Tático }),
    },
    {
      metric: "Técnico",
      [player1.name]: normalized1.Técnico,
      ...(normalized2 && { [player2.name]: normalized2.Técnico }),
    },
    {
      metric: "Físico",
      [player1.name]: normalized1.Físico,
      ...(normalized2 && { [player2.name]: normalized2.Físico }),
    },
    {
      metric: "Mental",
      [player1.name]: normalized1.Mental,
      ...(normalized2 && { [player2.name]: normalized2.Mental }),
    },
  ];

  return (
    <div className={cn("w-full", className)}>
      <ResponsiveContainer width="100%" height={height}>
        <RechartsRadar data={chartData}>
          <PolarGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: "#6B7280", fontSize: 12, fontWeight: 500 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: "#9CA3AF", fontSize: 10 }}
            tickCount={6}
          />

          {/* Radar do Jogador 1 */}
          <Radar
            name={player1.name}
            dataKey={player1.name}
            stroke={color1}
            fill={color1}
            fillOpacity={0.4}
            strokeWidth={2}
          />

          {/* Radar do Jogador 2 (se existir) */}
          {player2 && (
            <Radar
              name={player2.name}
              dataKey={player2.name}
              stroke={color2}
              fill={color2}
              fillOpacity={0.3}
              strokeWidth={2}
            />
          )}

          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{
              paddingTop: "20px",
              fontSize: "14px",
              fontWeight: 500,
            }}
            iconType="circle"
          />
        </RechartsRadar>
      </ResponsiveContainer>

      {/* Legenda de Escala */}
      <div className="mt-4 text-center text-xs text-gray-500">
        Escala: 0.0 (Muito Fraco) → 5.0 (Excepcional)
      </div>
    </div>
  );
}
