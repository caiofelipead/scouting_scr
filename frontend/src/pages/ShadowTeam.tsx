/**
 * Shadow Team Page - Scout Pro
 * Tactical formation builder with wishlist players
 */
import { useState } from "react";
import { Save, Trash2, Users as UsersIcon } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import api from "../lib/axios";
import { useShadowTeamStore, type Formation, type Position } from "../store/shadowTeamStore";
import PitchVisualization from "../components/pitch/PitchVisualization";
import Combobox from "../components/ui/Combobox";
import { Button } from "../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import type { JogadorWithDetails } from "../types";

export default function ShadowTeam() {
  const {
    formation,
    positions,
    setFormation,
    assignPlayer,
    clearAllPlayers,
  } = useShadowTeamStore();

  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null);

  // Fetch wishlist players
  const { data: wishlistData } = useQuery({
    queryKey: ["wishlist"],
    queryFn: async () => {
      const { data } = await api.get("/wishlist");
      return data;
    },
  });

  // Player options for combobox
  const playerOptions =
    wishlistData?.map((item: any) => ({
      value: item.jogador.id_jogador,
      label: `${item.jogador.nome} - ${item.jogador.posicao || "N/A"} (${
        item.prioridade
      })`,
      metadata: item.jogador,
    })) || [];

  // Handle position click
  const handlePositionClick = (position: Position) => {
    setSelectedPosition(position);
  };

  // Handle player assignment
  const handlePlayerSelect = (playerId: number | null) => {
    if (!selectedPosition) return;

    if (playerId === null) {
      // Clear position
      assignPlayer(selectedPosition.id, null);
      setSelectedPosition(null);
      return;
    }

    // Find player
    const option = playerOptions.find((opt: any) => opt.value === playerId);
    if (option) {
      assignPlayer(selectedPosition.id, option.metadata);
      toast.success(`${option.metadata.nome} atribuído à posição ${selectedPosition.role}`);
      setSelectedPosition(null);
    }
  };

  // Handle formation change
  const handleFormationChange = (newFormation: Formation) => {
    if (positions.some((pos) => pos.player !== null)) {
      if (
        !confirm(
          "Mudar a formação irá limpar todos os jogadores. Deseja continuar?"
        )
      ) {
        return;
      }
    }
    setFormation(newFormation);
    toast.info(`Formação alterada para ${newFormation}`);
  };

  // Save shadow team to backend
  const handleSave = async () => {
    try {
      const teamData = {
        formation,
        positions: positions
          .filter((pos) => pos.player !== null)
          .map((pos) => ({
            position_id: pos.id,
            position_role: pos.role,
            jogador_id: pos.player!.id_jogador,
          })),
      };

      await api.post("/shadow-teams", teamData);
      toast.success("Shadow Team salva com sucesso!");
    } catch (error) {
      toast.error("Erro ao salvar Shadow Team");
      console.error(error);
    }
  };

  // Clear all players
  const handleClearAll = () => {
    if (!confirm("Deseja realmente limpar todos os jogadores?")) return;
    clearAllPlayers();
    setSelectedPosition(null);
    toast.info("Todos os jogadores foram removidos");
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">Shadow Team</CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                Monte sua equipe tática ideal com jogadores da wishlist
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleClearAll}>
                <Trash2 className="h-4 w-4 mr-2" />
                Limpar Tudo
              </Button>
              <Button onClick={handleSave}>
                <Save className="h-4 w-4 mr-2" />
                Salvar
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Formation Selector */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Formation Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Formação Tática
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(["4-3-3", "4-4-2", "3-5-2"] as Formation[]).map((form) => (
                  <Button
                    key={form}
                    variant={formation === form ? "default" : "outline"}
                    onClick={() => handleFormationChange(form)}
                    className="w-full"
                  >
                    {form}
                  </Button>
                ))}
              </div>
            </div>

            {/* Player Assignment (when position selected) */}
            {selectedPosition && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Jogador para {selectedPosition.role}
                </label>
                <Combobox
                  options={playerOptions}
                  value={selectedPosition.player?.id_jogador}
                  onChange={handlePlayerSelect}
                  placeholder="Selecione um jogador da wishlist..."
                  emptyText="Nenhum jogador na wishlist"
                  clearable
                />
                <p className="text-xs text-gray-500 mt-2">
                  Clique em uma posição no campo para atribuir um jogador
                </p>
              </div>
            )}

            {!selectedPosition && (
              <div className="flex items-center justify-center bg-gray-50 rounded-lg p-6">
                <div className="text-center">
                  <UsersIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">
                    Clique em uma posição no campo para atribuir um jogador
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Pitch Visualization */}
      <Card>
        <CardHeader>
          <CardTitle>Campo Tático - {formation}</CardTitle>
        </CardHeader>
        <CardContent>
          <PitchVisualization
            onPositionClick={handlePositionClick}
            showLabels
            interactive
          />

          {/* Team Summary */}
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {positions.filter((p) => p.player !== null).length}
              </div>
              <div className="text-sm text-gray-600">Posições Preenchidas</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-400">
                {positions.filter((p) => p.player === null).length}
              </div>
              <div className="text-sm text-gray-600">Posições Vazias</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {positions.length}
              </div>
              <div className="text-sm text-gray-600">Total de Posições</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {wishlistData?.length || 0}
              </div>
              <div className="text-sm text-gray-600">Jogadores na Wishlist</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Squad List */}
      <Card>
        <CardHeader>
          <CardTitle>Escalação</CardTitle>
        </CardHeader>
        <CardContent>
          {positions.filter((p) => p.player !== null).length > 0 ? (
            <div className="space-y-2">
              {positions
                .filter((p) => p.player !== null)
                .map((pos) => (
                  <div
                    key={pos.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className="bg-blue-600 text-white font-bold px-3 py-1 rounded">
                        {pos.role}
                      </div>
                      <div>
                        <div className="font-medium">{pos.player!.nome}</div>
                        <div className="text-sm text-gray-600">
                          {pos.player!.posicao} - {pos.player!.clube || "Sem clube"}
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => assignPlayer(pos.id, null)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              Nenhum jogador atribuído ainda
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
