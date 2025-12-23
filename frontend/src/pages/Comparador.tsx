/**
 * Comparador Page - Scout Pro
 * Side-by-side player performance comparison
 */
import { useState } from "react";
import { ArrowLeftRight, Download, Users } from "lucide-react";
import { useJogadores } from "../hooks/useJogadores";
import { useMediaAvaliacoes } from "../hooks/useAvaliacoes";
import RadarChart from "../components/charts/RadarChart";
import Combobox from "../components/ui/Combobox";
import { Button } from "../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { formatNota, getMediaColor } from "../lib/utils";
import type { JogadorWithDetails } from "../types";

export default function Comparador() {
  const [player1Id, setPlayer1Id] = useState<number | null>(null);
  const [player2Id, setPlayer2Id] = useState<number | null>(null);

  // Fetch all players for combobox
  const { data: jogadoresData } = useJogadores({ limit: 1000 });

  // Fetch selected players' averages
  const { data: media1 } = useMediaAvaliacoes(player1Id || 0);
  const { data: media2 } = useMediaAvaliacoes(player2Id || 0);

  // Get player details
  const player1 = jogadoresData?.data.find((j) => j.id_jogador === player1Id);
  const player2 = jogadoresData?.data.find((j) => j.id_jogador === player2Id);

  // Combobox options
  const options =
    jogadoresData?.data.map((j) => ({
      value: j.id_jogador,
      label: `${j.nome} - ${j.posicao || "N/A"} (${j.clube || "Sem clube"})`,
    })) || [];

  // Invert comparison
  const handleInvert = () => {
    const temp = player1Id;
    setPlayer1Id(player2Id);
    setPlayer2Id(temp);
  };

  // Export PDF (placeholder)
  const handleExportPDF = () => {
    alert("Funcionalidade de exportação PDF será implementada em breve!");
    // TODO: Implement PDF export with jsPDF or similar
  };

  // Check if comparison is ready
  const isComparisonReady = player1 && player2 && media1 && media2;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">Comparador de Performance</CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                Compare até 2 jogadores lado a lado
              </p>
            </div>
            {isComparisonReady && (
              <div className="flex gap-2">
                <Button variant="outline" onClick={handleInvert}>
                  <ArrowLeftRight className="h-4 w-4 mr-2" />
                  Inverter
                </Button>
                <Button onClick={handleExportPDF}>
                  <Download className="h-4 w-4 mr-2" />
                  Exportar PDF
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
      </Card>

      {/* Player Selection */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Player 1 Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Jogador 1
              </label>
              <Combobox
                options={options}
                value={player1Id || undefined}
                onChange={(val) => setPlayer1Id(val as number)}
                placeholder="Selecione o primeiro jogador..."
                clearable
              />
            </div>

            {/* Player 2 Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Jogador 2
              </label>
              <Combobox
                options={options}
                value={player2Id || undefined}
                onChange={(val) => setPlayer2Id(val as number)}
                placeholder="Selecione o segundo jogador..."
                clearable
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Comparison View */}
      {isComparisonReady ? (
        <>
          {/* Radar Chart Comparison */}
          <Card>
            <CardHeader>
              <CardTitle>Comparação de Dimensões</CardTitle>
            </CardHeader>
            <CardContent>
              <RadarChart
                player1={{
                  name: player1.nome,
                  metrics: {
                    potencial: media1.potencial,
                    tatico: media1.tatico,
                    tecnico: media1.tecnico,
                    fisico: media1.fisico,
                    mental: media1.mental,
                  },
                  color: "#3B82F6", // Blue
                }}
                player2={{
                  name: player2.nome,
                  metrics: {
                    potencial: media2.potencial,
                    tatico: media2.tatico,
                    tecnico: media2.tecnico,
                    fisico: media2.fisico,
                    mental: media2.mental,
                  },
                  color: "#FBBF24", // Yellow
                }}
                height={450}
              />
            </CardContent>
          </Card>

          {/* Side-by-Side Table */}
          <Card>
            <CardHeader>
              <CardTitle>Comparação Lado a Lado</CardTitle>
            </CardHeader>
            <CardContent>
              <ComparisonTable player1={player1} player2={player2} media1={media1} media2={media2} />
            </CardContent>
          </Card>
        </>
      ) : (
        <Card>
          <CardContent className="py-16">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                <Users className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Selecione 2 Jogadores
              </h3>
              <p className="text-gray-600 max-w-md mx-auto">
                Escolha dois jogadores acima para visualizar a comparação de
                performance e métricas lado a lado.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/**
 * Comparison Table Component
 */
function ComparisonTable({
  player1,
  player2,
  media1,
  media2,
}: {
  player1: JogadorWithDetails;
  player2: JogadorWithDetails;
  media1: any;
  media2: any;
}) {
  // Calculate overall averages
  const avg1 =
    (media1.potencial +
      media1.tatico +
      media1.tecnico +
      media1.fisico +
      media1.mental) /
    5;
  const avg2 =
    (media2.potencial +
      media2.tatico +
      media2.tecnico +
      media2.fisico +
      media2.mental) /
    5;

  const rows = [
    {
      label: "Nome",
      value1: player1.nome,
      value2: player2.nome,
    },
    {
      label: "Idade",
      value1: player1.idade_atual || "N/A",
      value2: player2.idade_atual || "N/A",
      numeric: true,
    },
    {
      label: "Posição",
      value1: player1.posicao || "N/A",
      value2: player2.posicao || "N/A",
    },
    {
      label: "Clube",
      value1: player1.clube || "Sem clube",
      value2: player2.clube || "Sem clube",
    },
    {
      label: "Valor de Mercado",
      value1: player1.valor_mercado_euros
        ? `€${(player1.valor_mercado_euros / 1_000_000).toFixed(1)}M`
        : "N/A",
      value2: player2.valor_mercado_euros
        ? `€${(player2.valor_mercado_euros / 1_000_000).toFixed(1)}M`
        : "N/A",
    },
    {
      label: "Contrato até",
      value1: player1.contrato_ate || "N/A",
      value2: player2.contrato_ate || "N/A",
    },
    { divider: true },
    {
      label: "Potencial",
      value1: formatNota(media1.potencial),
      value2: formatNota(media2.potencial),
      color1: getMediaColor(media1.potencial),
      color2: getMediaColor(media2.potencial),
    },
    {
      label: "Tático",
      value1: formatNota(media1.tatico),
      value2: formatNota(media1.tatico),
      color1: getMediaColor(media1.tatico),
      color2: getMediaColor(media2.tatico),
    },
    {
      label: "Técnico",
      value1: formatNota(media1.tecnico),
      value2: formatNota(media2.tecnico),
      color1: getMediaColor(media1.tecnico),
      color2: getMediaColor(media2.tecnico),
    },
    {
      label: "Físico",
      value1: formatNota(media1.fisico),
      value2: formatNota(media2.fisico),
      color1: getMediaColor(media1.fisico),
      color2: getMediaColor(media2.fisico),
    },
    {
      label: "Mental",
      value1: formatNota(media1.mental),
      value2: formatNota(media2.mental),
      color1: getMediaColor(media1.mental),
      color2: getMediaColor(media2.mental),
    },
    { divider: true },
    {
      label: "Média Geral",
      value1: formatNota(avg1),
      value2: formatNota(avg2),
      color1: getMediaColor(avg1),
      color2: getMediaColor(avg2),
      highlight: true,
    },
  ];

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase">
              Atributo
            </th>
            <th className="px-4 py-3 text-center text-xs font-semibold text-blue-600 uppercase">
              {player1.nome}
            </th>
            <th className="px-4 py-3 text-center text-xs font-semibold text-yellow-600 uppercase">
              {player2.nome}
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {rows.map((row, index) => {
            if (row.divider) {
              return (
                <tr key={`divider-${index}`}>
                  <td colSpan={3} className="h-2 bg-gray-50" />
                </tr>
              );
            }

            return (
              <tr
                key={row.label}
                className={row.highlight ? "bg-blue-50" : ""}
              >
                <td className="px-4 py-3 text-sm font-medium text-gray-900">
                  {row.label}
                </td>
                <td
                  className={`px-4 py-3 text-sm text-center ${
                    row.color1 || "text-gray-700"
                  } ${row.highlight ? "font-bold" : ""}`}
                >
                  {row.value1}
                </td>
                <td
                  className={`px-4 py-3 text-sm text-center ${
                    row.color2 || "text-gray-700"
                  } ${row.highlight ? "font-bold" : ""}`}
                >
                  {row.value2}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
