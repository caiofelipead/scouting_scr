/**
 * Página Jogadores - Scout Pro
 * Listagem avançada de jogadores com TanStack Table
 */
import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  flexRender,
  createColumnHelper,
  SortingState,
} from "@tanstack/react-table";
import { Eye, Edit, UserPlus, ArrowUpDown, Users } from "lucide-react";
import { useJogadores } from "../hooks/useJogadores";
import { formatNota, getMediaColor, calcularMedia } from "../lib/utils";
import type { JogadorWithDetails, JogadorFilters } from "../types";
import SearchInput from "../components/ui/SearchInput";
import { Button } from "../components/ui/Button";
import { TableSkeleton } from "../components/ui/Skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";

const columnHelper = createColumnHelper<JogadorWithDetails>();

export default function Jogadores() {
  const navigate = useNavigate();

  // Estado de filtros
  const [filters, setFilters] = useState<JogadorFilters>({
    page: 1,
    limit: 50,
  });

  // Estado de ordenação
  const [sorting, setSorting] = useState<SortingState>([]);

  // Hook de dados
  const { data, isLoading, isError } = useJogadores(filters);

  // Definição de colunas
  const columns = useMemo(
    () => [
      // Foto
      columnHelper.accessor("transfermarkt_id", {
        header: "Foto",
        cell: (info) => {
          const tmId = info.getValue();
          // URL padrão de foto do Transfermarkt (ou placeholder)
          const photoUrl = tmId
            ? `https://img.a.transfermarkt.technology/portrait/header/${tmId}.jpg`
            : "/placeholder-player.png";

          return (
            <div className="flex items-center justify-center">
              <img
                src={photoUrl}
                alt={info.row.original.nome}
                className="h-10 w-10 rounded-full object-cover border border-gray-200"
                onError={(e) => {
                  // Fallback para placeholder se imagem falhar
                  e.currentTarget.src = "/placeholder-player.png";
                }}
              />
            </div>
          );
        },
        enableSorting: false,
      }),

      // Nome
      columnHelper.accessor("nome", {
        header: ({ column }) => (
          <button
            onClick={() => column.toggleSorting()}
            className="flex items-center gap-1 hover:text-blue-600 transition-colors"
          >
            Nome
            <ArrowUpDown className="h-3 w-3" />
          </button>
        ),
        cell: (info) => (
          <div className="font-medium text-gray-900">{info.getValue()}</div>
        ),
      }),

      // Idade
      columnHelper.accessor("idade_atual", {
        header: ({ column }) => (
          <button
            onClick={() => column.toggleSorting()}
            className="flex items-center gap-1 hover:text-blue-600 transition-colors"
          >
            Idade
            <ArrowUpDown className="h-3 w-3" />
          </button>
        ),
        cell: (info) => (
          <div className="text-gray-700">
            {info.getValue() || "N/A"}
          </div>
        ),
      }),

      // Posição
      columnHelper.accessor("posicao", {
        header: "Posição",
        cell: (info) => {
          const posicao = info.getValue();
          return (
            <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {posicao || "N/A"}
            </div>
          );
        },
      }),

      // Clube
      columnHelper.accessor("clube", {
        header: "Clube",
        cell: (info) => (
          <div className="text-gray-700 max-w-[200px] truncate">
            {info.getValue() || "Sem clube"}
          </div>
        ),
      }),

      // Média Geral
      columnHelper.display({
        id: "media_geral",
        header: ({ column }) => (
          <button
            onClick={() => column.toggleSorting()}
            className="flex items-center gap-1 hover:text-blue-600 transition-colors"
          >
            Média Geral
            <ArrowUpDown className="h-3 w-3" />
          </button>
        ),
        cell: ({ row }) => {
          const jogador = row.original;
          const media = calcularMedia([
            jogador.nota_potencial_media,
          ]);
          const mediaColor = getMediaColor(media);

          return (
            <div className={`font-semibold ${mediaColor}`}>
              {formatNota(media)}
            </div>
          );
        },
      }),

      // Ações
      columnHelper.display({
        id: "acoes",
        header: "Ações",
        cell: ({ row }) => {
          const jogador = row.original;
          return (
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate(`/jogadores/${jogador.id_jogador}`)}
              >
                <Eye className="h-3 w-3 mr-1" />
                Ver
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate(`/jogadores/${jogador.id_jogador}/editar`)}
              >
                <Edit className="h-3 w-3 mr-1" />
                Editar
              </Button>
            </div>
          );
        },
      }),
    ],
    [navigate]
  );

  // Configuração da tabela
  const table = useReactTable({
    data: data?.data || [],
    columns,
    state: {
      sorting,
    },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  // Renderização de estados
  if (isError) {
    return (
      <div className="p-6">
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <div className="text-red-600 text-lg font-semibold mb-2">
                Erro ao carregar jogadores
              </div>
              <p className="text-gray-600 mb-4">
                Não foi possível buscar os dados. Tente novamente.
              </p>
              <Button onClick={() => window.location.reload()}>
                Recarregar
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const hasData = data && data.data.length > 0;
  const isEmpty = !isLoading && !hasData;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">Jogadores</CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                {data?.total || 0} jogadores cadastrados
              </p>
            </div>
            <Button onClick={() => navigate("/jogadores/novo")}>
              <UserPlus className="h-4 w-4 mr-2" />
              Novo Jogador
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <SearchInput
              placeholder="Buscar por nome..."
              onSearch={(query) =>
                setFilters({ ...filters, nome: query, page: 1 })
              }
              className="md:col-span-2"
            />
            {/* TODO: Adicionar mais filtros (Posição, Clube, etc.) */}
          </div>
        </CardContent>
      </Card>

      {/* Tabela */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <th
                        key={header.id}
                        className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                      >
                        {header.isPlaceholder
                          ? null
                          : flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {isLoading ? (
                  <TableSkeleton rows={10} />
                ) : isEmpty ? (
                  <tr>
                    <td colSpan={columns.length} className="px-4 py-16">
                      <EmptyState
                        onClear={() => setFilters({ page: 1, limit: 50 })}
                        hasFilters={!!filters.nome}
                      />
                    </td>
                  </tr>
                ) : (
                  table.getRowModel().rows.map((row) => (
                    <tr
                      key={row.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      {row.getVisibleCells().map((cell) => (
                        <td key={cell.id} className="px-4 py-3">
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext()
                          )}
                        </td>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Paginação */}
          {hasData && (
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Página {data.page} de {data.pages} • {data.total} total
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setFilters({ ...filters, page: filters.page! - 1 })
                  }
                  disabled={filters.page === 1}
                >
                  Anterior
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() =>
                    setFilters({ ...filters, page: filters.page! + 1 })
                  }
                  disabled={filters.page === data.pages}
                >
                  Próxima
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Empty State - Exibido quando não há jogadores
 */
function EmptyState({
  onClear,
  hasFilters,
}: {
  onClear: () => void;
  hasFilters: boolean;
}) {
  return (
    <div className="text-center py-12">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
        <Users className="h-8 w-8 text-gray-400" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {hasFilters ? "Nenhum jogador encontrado" : "Nenhum jogador cadastrado"}
      </h3>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">
        {hasFilters
          ? "Tente ajustar os filtros de busca para encontrar o que procura."
          : "Comece adicionando jogadores ao sistema de scouting."}
      </p>
      {hasFilters ? (
        <Button variant="outline" onClick={onClear}>
          Limpar Filtros
        </Button>
      ) : (
        <Button onClick={() => {}}>
          <UserPlus className="h-4 w-4 mr-2" />
          Adicionar Primeiro Jogador
        </Button>
      )}
    </div>
  );
}
