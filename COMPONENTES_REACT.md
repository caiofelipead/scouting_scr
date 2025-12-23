# ⚛️ COMPONENTES REACT - SCOUT PRO

## Exemplo de Componente Principal: Dashboard de Jogadores

Este é o componente principal que substitui a visualização tabular/cards do Streamlit.

### `frontend/src/pages/Jogadores.tsx`

```typescript
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Search,
  Filter,
  Download,
  Grid3x3,
  Table as TableIcon,
  Star,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

import { getJogadores } from '@/services/jogadores';
import { useFilterStore } from '@/store/filterStore';
import { useDebounce } from '@/hooks/useDebounce';

import JogadorCard from '@/components/jogador/JogadorCard';
import JogadorTable from '@/components/jogador/JogadorTable';
import FilterPanel from '@/components/jogador/FilterPanel';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loading } from '@/components/common/Loading';

type ViewMode = 'cards' | 'table';

export default function Jogadores() {
  // Estado local
  const [viewMode, setViewMode] = useState<ViewMode>('cards');
  const [page, setPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const limit = 50;

  // Estado global (Zustand)
  const {
    posicoes,
    clubes,
    ligas,
    nacionalidades,
    idadeMin,
    idadeMax,
    mediaMin,
    buscaNome,
    setBuscaNome,
    resetFilters,
    getApiFilters
  } = useFilterStore();

  // Debounce da busca por nome
  const debouncedBuscaNome = useDebounce(buscaNome, 500);

  // Fetch de jogadores com React Query
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['jogadores', page, debouncedBuscaNome, posicoes, clubes, ligas,
               nacionalidades, idadeMin, idadeMax, mediaMin],
    queryFn: () => getJogadores({
      ...getApiFilters(),
      page,
      limit
    }),
    keepPreviousData: true,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  // Handlers
  const handleExportCSV = () => {
    if (!data?.data) return;

    const csvContent = [
      ['Nome', 'Posição', 'Clube', 'Idade', 'Nacionalidade', 'Média Geral'].join(','),
      ...data.data.map(j => [
        j.nome,
        j.posicao,
        j.clube,
        j.idade_atual,
        j.nacionalidade,
        j.media_geral || 'N/A'
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `jogadores_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const totalFiltrosAtivos = [
    posicoes.length,
    clubes.length,
    ligas.length,
    nacionalidades.length,
    idadeMin !== 16 || idadeMax !== 40 ? 1 : 0,
    mediaMin > 0 ? 1 : 0
  ].reduce((a, b) => a + b, 0);

  // Renderização
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            {/* Título e Stats */}
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Jogadores</h1>
              <p className="text-sm text-gray-500 mt-1">
                {isLoading ? (
                  'Carregando...'
                ) : (
                  <>
                    {data?.total || 0} jogadores encontrados
                    {totalFiltrosAtivos > 0 && (
                      <span className="ml-2">
                        ({totalFiltrosAtivos} {totalFiltrosAtivos === 1 ? 'filtro' : 'filtros'} aplicado{totalFiltrosAtivos === 1 ? '' : 's'})
                      </span>
                    )}
                  </>
                )}
              </p>
            </div>

            {/* Ações */}
            <div className="flex items-center gap-2 w-full sm:w-auto">
              {/* Busca */}
              <div className="relative flex-1 sm:flex-none sm:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Buscar por nome..."
                  value={buscaNome}
                  onChange={(e) => setBuscaNome(e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* Filtros */}
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
                className="relative"
              >
                <Filter className="h-4 w-4 mr-2" />
                Filtros
                {totalFiltrosAtivos > 0 && (
                  <Badge
                    variant="destructive"
                    className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
                  >
                    {totalFiltrosAtivos}
                  </Badge>
                )}
              </Button>

              {/* Export CSV */}
              <Button variant="outline" onClick={handleExportCSV}>
                <Download className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Exportar</span>
              </Button>

              {/* Modo de Visualização */}
              <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as ViewMode)}>
                <TabsList>
                  <TabsTrigger value="cards">
                    <Grid3x3 className="h-4 w-4" />
                  </TabsTrigger>
                  <TabsTrigger value="table">
                    <TableIcon className="h-4 w-4" />
                  </TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </div>

          {/* Filtros Ativos (Pills) */}
          {totalFiltrosAtivos > 0 && (
            <div className="flex items-center gap-2 mt-4 flex-wrap">
              <span className="text-sm text-gray-500">Filtros ativos:</span>
              {posicoes.map(pos => (
                <Badge key={pos} variant="secondary">{pos}</Badge>
              ))}
              {clubes.map(clube => (
                <Badge key={clube} variant="secondary">{clube}</Badge>
              ))}
              {ligas.map(liga => (
                <Badge key={liga} variant="secondary">{liga}</Badge>
              ))}
              {(idadeMin !== 16 || idadeMax !== 40) && (
                <Badge variant="secondary">Idade: {idadeMin}-{idadeMax}</Badge>
              )}
              {mediaMin > 0 && (
                <Badge variant="secondary">Média ≥ {mediaMin}</Badge>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={resetFilters}
                className="text-xs text-red-600"
              >
                Limpar filtros
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Painel de Filtros (Lateral) */}
      {showFilters && (
        <div className="fixed inset-0 bg-black/50 z-20" onClick={() => setShowFilters(false)}>
          <div
            className="absolute right-0 top-0 h-full w-96 bg-white shadow-2xl overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <FilterPanel onClose={() => setShowFilters(false)} />
          </div>
        </div>
      )}

      {/* Conteúdo Principal */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-96">
            <Loading />
          </div>
        ) : isError ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-800">
              Erro ao carregar jogadores: {error instanceof Error ? error.message : 'Erro desconhecido'}
            </p>
          </div>
        ) : data?.data.length === 0 ? (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
            <p className="text-gray-500 text-lg">Nenhum jogador encontrado com os filtros aplicados</p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={resetFilters}
            >
              Limpar filtros
            </Button>
          </div>
        ) : (
          <>
            {/* Grid de Cards ou Tabela */}
            {viewMode === 'cards' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {data?.data.map((jogador) => (
                  <JogadorCard key={jogador.id_jogador} jogador={jogador} />
                ))}
              </div>
            ) : (
              <JogadorTable jogadores={data?.data || []} />
            )}

            {/* Paginação */}
            <div className="mt-8 flex items-center justify-between border-t pt-4">
              <div className="text-sm text-gray-500">
                Mostrando {(page - 1) * limit + 1} a {Math.min(page * limit, data?.total || 0)} de {data?.total || 0} jogadores
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Anterior
                </Button>

                <div className="flex items-center gap-1">
                  {Array.from({ length: Math.min(5, data?.pages || 0) }, (_, i) => {
                    const pageNum = i + 1;
                    return (
                      <Button
                        key={pageNum}
                        variant={page === pageNum ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setPage(pageNum)}
                        className="w-10"
                      >
                        {pageNum}
                      </Button>
                    );
                  })}
                  {(data?.pages || 0) > 5 && (
                    <>
                      <span className="text-gray-500 px-2">...</span>
                      <Button
                        variant={page === data?.pages ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setPage(data?.pages || 1)}
                        className="w-10"
                      >
                        {data?.pages}
                      </Button>
                    </>
                  )}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => Math.min(data?.pages || 1, p + 1))}
                  disabled={page === data?.pages}
                >
                  Próxima
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
```

---

## Componente: JogadorCard

### `frontend/src/components/jogador/JogadorCard.tsx`

```typescript
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Star, StarOff, MapPin, Calendar, TrendingUp, User } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { addToWishlist, removeFromWishlist } from '@/services/wishlist';
import { toast } from 'react-hot-toast';

import type { Jogador } from '@/types/jogador';

interface JogadorCardProps {
  jogador: Jogador;
}

export default function JogadorCard({ jogador }: JogadorCardProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Mutation para wishlist
  const wishlistMutation = useMutation({
    mutationFn: (isAdding: boolean) =>
      isAdding
        ? addToWishlist({ id_jogador: jogador.id_jogador, prioridade: 'media' })
        : removeFromWishlist(jogador.id_jogador),
    onSuccess: (_, isAdding) => {
      queryClient.invalidateQueries(['jogadores']);
      toast.success(isAdding ? 'Adicionado à wishlist' : 'Removido da wishlist');
    },
    onError: () => {
      toast.error('Erro ao atualizar wishlist');
    }
  });

  const handleWishlistToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    wishlistMutation.mutate(!jogador.na_wishlist);
  };

  const handleCardClick = () => {
    navigate(`/jogadores/${jogador.id_jogador}`);
  };

  // Helper para cor da média
  const getMediaColor = (media: number | null) => {
    if (!media) return 'text-gray-400';
    if (media >= 4.5) return 'text-green-600';
    if (media >= 3.5) return 'text-blue-600';
    if (media >= 2.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Helper para cor da posição
  const getPosicaoColor = (posicao: string) => {
    const cores: Record<string, string> = {
      'GOL': 'bg-yellow-100 text-yellow-800',
      'LAD': 'bg-blue-100 text-blue-800',
      'LAE': 'bg-blue-100 text-blue-800',
      'ZAG': 'bg-green-100 text-green-800',
      'VOL': 'bg-purple-100 text-purple-800',
      'MEI': 'bg-indigo-100 text-indigo-800',
      'ATA': 'bg-red-100 text-red-800'
    };
    return cores[posicao] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Card
      className="group hover:shadow-xl transition-all duration-300 cursor-pointer overflow-hidden"
      onClick={handleCardClick}
    >
      {/* Foto de Capa */}
      <div className="relative h-48 bg-gradient-to-br from-gray-100 to-gray-200 overflow-hidden">
        {jogador.foto_url ? (
          <img
            src={jogador.foto_url}
            alt={jogador.nome}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <User className="h-24 w-24 text-gray-300" />
          </div>
        )}

        {/* Overlay com Wishlist */}
        <div className="absolute top-2 right-2">
          <Button
            variant="secondary"
            size="sm"
            className="rounded-full w-9 h-9 p-0 bg-white/90 hover:bg-white shadow-lg"
            onClick={handleWishlistToggle}
          >
            {jogador.na_wishlist ? (
              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
            ) : (
              <StarOff className="h-4 w-4 text-gray-400" />
            )}
          </Button>
        </div>

        {/* Badge de Posição */}
        <div className="absolute bottom-2 left-2">
          <Badge className={getPosicaoColor(jogador.posicao)}>
            {jogador.posicao}
          </Badge>
        </div>

        {/* Badge de Média */}
        {jogador.media_geral && (
          <div className="absolute bottom-2 right-2">
            <div className="bg-white/90 rounded-full px-3 py-1 font-bold text-sm shadow-lg">
              <span className={getMediaColor(jogador.media_geral)}>
                {jogador.media_geral.toFixed(1)}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Conteúdo */}
      <CardContent className="p-4">
        {/* Nome */}
        <h3 className="font-bold text-lg text-gray-900 truncate mb-2">
          {jogador.nome}
        </h3>

        {/* Informações */}
        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-gray-400" />
            <span className="truncate">{jogador.clube}</span>
          </div>

          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-gray-400" />
            <span>
              {jogador.idade_atual} anos · {jogador.nacionalidade}
            </span>
          </div>

          {jogador.ultima_avaliacao && (
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-gray-400" />
              <div className="flex gap-1 text-xs">
                <span>Pot: {jogador.ultima_avaliacao.nota_potencial}</span>
                <span>·</span>
                <span>Tát: {jogador.ultima_avaliacao.nota_tatico}</span>
                <span>·</span>
                <span>Téc: {jogador.ultima_avaliacao.nota_tecnico}</span>
              </div>
            </div>
          )}
        </div>

        {/* Tags */}
        {jogador.tags && jogador.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-3">
            {jogador.tags.slice(0, 3).map(tag => (
              <Badge
                key={tag.id_tag}
                variant="outline"
                style={{
                  borderColor: tag.cor,
                  color: tag.cor
                }}
                className="text-xs"
              >
                {tag.nome}
              </Badge>
            ))}
            {jogador.tags.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{jogador.tags.length - 3}
              </Badge>
            )}
          </div>
        )}
      </CardContent>

      {/* Footer */}
      <CardFooter className="p-4 pt-0 border-t bg-gray-50">
        <div className="flex items-center justify-between w-full text-xs text-gray-500">
          <span>{jogador.liga_clube}</span>
          {jogador.status_contrato === 'Vencendo' && (
            <Badge variant="destructive" className="text-xs">
              Contrato vencendo
            </Badge>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}
```

---

## Componente: RadarChart (Avaliação)

### `frontend/src/components/charts/RadarChart.tsx`

```typescript
import React from 'react';
import {
  Radar,
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip
} from 'recharts';

interface RadarChartProps {
  data: Array<{
    categoria: string;
    [key: string]: number | string;
  }>;
  series: string[];
  colors?: string[];
  height?: number;
}

const defaultColors = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // amber
];

export default function RadarChart({
  data,
  series,
  colors = defaultColors,
  height = 400
}: RadarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsRadar data={data}>
        <PolarGrid strokeDasharray="3 3" />
        <PolarAngleAxis
          dataKey="categoria"
          tick={{ fill: '#6b7280', fontSize: 12 }}
        />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 5]}
          tick={{ fill: '#6b7280', fontSize: 10 }}
        />

        {series.map((serie, index) => (
          <Radar
            key={serie}
            name={serie}
            dataKey={serie}
            stroke={colors[index % colors.length]}
            fill={colors[index % colors.length]}
            fillOpacity={0.2}
            strokeWidth={2}
          />
        ))}

        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
          }}
        />
        <Legend
          wrapperStyle={{
            paddingTop: '20px'
          }}
        />
      </RechartsRadar>
    </ResponsiveContainer>
  );
}
```

**Exemplo de uso:**

```typescript
// Comparador de 3 jogadores
const radarData = [
  {
    categoria: 'Potencial',
    'Neymar': 5.0,
    'Vinicius Jr.': 5.0,
    'Rodrygo': 4.5
  },
  {
    categoria: 'Tático',
    'Neymar': 4.5,
    'Vinicius Jr.': 4.5,
    'Rodrygo': 4.0
  },
  {
    categoria: 'Técnico',
    'Neymar': 5.0,
    'Vinicius Jr.': 4.5,
    'Rodrygo': 4.5
  },
  {
    categoria: 'Físico',
    'Neymar': 4.5,
    'Vinicius Jr.': 5.0,
    'Rodrygo': 4.5
  },
  {
    categoria: 'Mental',
    'Neymar': 5.0,
    'Vinicius Jr.': 4.5,
    'Rodrygo': 4.5
  }
];

<RadarChart
  data={radarData}
  series={['Neymar', 'Vinicius Jr.', 'Rodrygo']}
  colors={['#3b82f6', '#10b981', '#f59e0b']}
/>
```

---

## Componente: EvolucaoChart (Linha Temporal)

### `frontend/src/components/charts/EvolucaoChart.tsx`

```typescript
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface EvolucaoData {
  data_avaliacao: string;
  nota_potencial: number;
  nota_tatico: number;
  nota_tecnico: number;
  nota_fisico: number;
  nota_mental: number;
  media_geral: number;
}

interface EvolucaoChartProps {
  data: EvolucaoData[];
  height?: number;
}

export default function EvolucaoChart({ data, height = 400 }: EvolucaoChartProps) {
  // Formatar datas
  const formattedData = data.map(item => ({
    ...item,
    data: format(new Date(item.data_avaliacao), 'dd/MM/yy', { locale: ptBR })
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={formattedData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />

        <XAxis
          dataKey="data"
          tick={{ fill: '#6b7280', fontSize: 12 }}
          stroke="#9ca3af"
        />

        <YAxis
          domain={[0, 5]}
          tick={{ fill: '#6b7280', fontSize: 12 }}
          stroke="#9ca3af"
        />

        <Tooltip
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
          }}
          labelStyle={{ fontWeight: 'bold', marginBottom: '8px' }}
        />

        <Legend
          wrapperStyle={{ paddingTop: '20px' }}
          iconType="line"
        />

        <Line
          type="monotone"
          dataKey="nota_potencial"
          name="Potencial"
          stroke="#8b5cf6"
          strokeWidth={2}
          dot={{ r: 4 }}
          activeDot={{ r: 6 }}
        />

        <Line
          type="monotone"
          dataKey="nota_tatico"
          name="Tático"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={{ r: 4 }}
          activeDot={{ r: 6 }}
        />

        <Line
          type="monotone"
          dataKey="nota_tecnico"
          name="Técnico"
          stroke="#10b981"
          strokeWidth={2}
          dot={{ r: 4 }}
          activeDot={{ r: 6 }}
        />

        <Line
          type="monotone"
          dataKey="nota_fisico"
          name="Físico"
          stroke="#f59e0b"
          strokeWidth={2}
          dot={{ r: 4 }}
          activeDot={{ r: 6 }}
        />

        <Line
          type="monotone"
          dataKey="nota_mental"
          name="Mental"
          stroke="#ef4444"
          strokeWidth={2}
          dot={{ r: 4 }}
          activeDot={{ r: 6 }}
        />

        <Line
          type="monotone"
          dataKey="media_geral"
          name="Média Geral"
          stroke="#000"
          strokeWidth={3}
          dot={{ r: 5 }}
          activeDot={{ r: 7 }}
          strokeDasharray="5 5"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

---

## Componente: FilterPanel

### `frontend/src/components/jogador/FilterPanel.tsx`

```typescript
import React from 'react';
import { X, RotateCcw } from 'lucide-react';
import { useFilterStore } from '@/store/filterStore';
import { useQuery } from '@tanstack/react-query';

import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';

import { getFilterOptions } from '@/services/jogadores';

interface FilterPanelProps {
  onClose: () => void;
}

export default function FilterPanel({ onClose }: FilterPanelProps) {
  const {
    posicoes,
    setPosicoes,
    clubes,
    setClubes,
    ligas,
    setLigas,
    nacionalidades,
    setNacionalidades,
    idadeMin,
    idadeMax,
    setIdadeRange,
    mediaMin,
    setMediaMin,
    resetFilters
  } = useFilterStore();

  // Buscar opções de filtros (listas únicas de clubes, ligas, etc)
  const { data: filterOptions } = useQuery({
    queryKey: ['filterOptions'],
    queryFn: getFilterOptions,
    staleTime: Infinity // Não muda com frequência
  });

  const posicoesDisponiveis = ['GOL', 'LAD', 'LAE', 'ZAG', 'VOL', 'MEI', 'ATA'];

  const togglePosicao = (pos: string) => {
    setPosicoes(
      posicoes.includes(pos)
        ? posicoes.filter(p => p !== pos)
        : [...posicoes, pos]
    );
  };

  const toggleClube = (clube: string) => {
    setClubes(
      clubes.includes(clube)
        ? clubes.filter(c => c !== clube)
        : [...clubes, clube]
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-gray-50">
        <h2 className="text-lg font-bold">Filtros</h2>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={resetFilters}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Limpar
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Conteúdo */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Posição */}
        <div>
          <Label className="text-sm font-semibold mb-3 block">Posição</Label>
          <div className="flex flex-wrap gap-2">
            {posicoesDisponiveis.map(pos => (
              <Button
                key={pos}
                variant={posicoes.includes(pos) ? 'default' : 'outline'}
                size="sm"
                onClick={() => togglePosicao(pos)}
              >
                {pos}
              </Button>
            ))}
          </div>
        </div>

        {/* Clube */}
        <div>
          <Label className="text-sm font-semibold mb-3 block">
            Clube ({clubes.length} selecionados)
          </Label>
          <div className="space-y-2 max-h-64 overflow-y-auto border rounded-lg p-3">
            {filterOptions?.clubes.slice(0, 50).map(clube => (
              <div key={clube} className="flex items-center gap-2">
                <Checkbox
                  id={`clube-${clube}`}
                  checked={clubes.includes(clube)}
                  onCheckedChange={() => toggleClube(clube)}
                />
                <Label
                  htmlFor={`clube-${clube}`}
                  className="text-sm cursor-pointer flex-1"
                >
                  {clube}
                </Label>
              </div>
            ))}
          </div>
        </div>

        {/* Liga */}
        <div>
          <Label className="text-sm font-semibold mb-3 block">Liga</Label>
          <div className="space-y-2">
            {filterOptions?.ligas.slice(0, 20).map(liga => (
              <div key={liga} className="flex items-center gap-2">
                <Checkbox
                  id={`liga-${liga}`}
                  checked={ligas.includes(liga)}
                  onCheckedChange={() => {
                    setLigas(
                      ligas.includes(liga)
                        ? ligas.filter(l => l !== liga)
                        : [...ligas, liga]
                    );
                  }}
                />
                <Label
                  htmlFor={`liga-${liga}`}
                  className="text-sm cursor-pointer flex-1"
                >
                  {liga}
                </Label>
              </div>
            ))}
          </div>
        </div>

        {/* Idade */}
        <div>
          <Label className="text-sm font-semibold mb-3 block">
            Idade: {idadeMin} - {idadeMax} anos
          </Label>
          <div className="px-2">
            <Slider
              min={16}
              max={40}
              step={1}
              value={[idadeMin, idadeMax]}
              onValueChange={([min, max]) => setIdadeRange(min, max)}
              className="mb-2"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>16</span>
              <span>40</span>
            </div>
          </div>
        </div>

        {/* Média Mínima */}
        <div>
          <Label className="text-sm font-semibold mb-3 block">
            Média Mínima: {mediaMin > 0 ? mediaMin.toFixed(1) : 'Todas'}
          </Label>
          <div className="px-2">
            <Slider
              min={0}
              max={5}
              step={0.5}
              value={[mediaMin]}
              onValueChange={([value]) => setMediaMin(value)}
              className="mb-2"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0.0</span>
              <span>5.0</span>
            </div>
          </div>
        </div>

        {/* Nacionalidade */}
        <div>
          <Label className="text-sm font-semibold mb-3 block">
            Nacionalidade ({nacionalidades.length} selecionadas)
          </Label>
          <div className="space-y-2 max-h-48 overflow-y-auto border rounded-lg p-3">
            {filterOptions?.nacionalidades.slice(0, 30).map(nac => (
              <div key={nac} className="flex items-center gap-2">
                <Checkbox
                  id={`nac-${nac}`}
                  checked={nacionalidades.includes(nac)}
                  onCheckedChange={() => {
                    setNacionalidades(
                      nacionalidades.includes(nac)
                        ? nacionalidades.filter(n => n !== nac)
                        : [...nacionalidades, nac]
                    );
                  }}
                />
                <Label
                  htmlFor={`nac-${nac}`}
                  className="text-sm cursor-pointer flex-1"
                >
                  {nac}
                </Label>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t bg-gray-50">
        <Button
          className="w-full"
          onClick={onClose}
        >
          Aplicar Filtros
        </Button>
      </div>
    </div>
  );
}
```

---

## Componente: PitchVisualization (Shadow Team)

### `frontend/src/components/pitch/PitchVisualization.tsx`

```typescript
import React from 'react';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Card } from '@/components/ui/card';

interface Jogador {
  id_jogador: number;
  nome: string;
  foto_url?: string;
  posicao: string;
}

interface JogadorPosicionado {
  posicao_campo: string;
  coordenada_x: number;
  coordenada_y: number;
  jogador: Jogador;
}

interface PitchVisualizationProps {
  formacao: '4-4-2' | '4-3-3' | '3-5-2' | '4-2-3-1';
  jogadores: JogadorPosicionado[];
  width?: number;
  height?: number;
}

export default function PitchVisualization({
  formacao,
  jogadores,
  width = 700,
  height = 500
}: PitchVisualizationProps) {
  return (
    <Card className="p-4 bg-gradient-to-br from-green-600 to-green-700">
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto"
      >
        {/* Fundo do campo */}
        <rect
          x="0"
          y="0"
          width={width}
          height={height}
          fill="url(#grass-gradient)"
        />

        {/* Gradiente do gramado */}
        <defs>
          <linearGradient id="grass-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="50%" stopColor="#059669" />
            <stop offset="100%" stopColor="#10b981" />
          </linearGradient>
        </defs>

        {/* Linhas do campo */}
        <g stroke="rgba(255,255,255,0.3)" strokeWidth="2" fill="none">
          {/* Borda */}
          <rect x="20" y="20" width={width - 40} height={height - 40} />

          {/* Linha do meio */}
          <line
            x1={width / 2}
            y1="20"
            x2={width / 2}
            y2={height - 20}
          />

          {/* Círculo central */}
          <circle
            cx={width / 2}
            cy={height / 2}
            r="60"
          />

          {/* Área grande (superior) */}
          <rect
            x={width / 2 - 100}
            y="20"
            width="200"
            height="80"
          />

          {/* Área pequena (superior) */}
          <rect
            x={width / 2 - 60}
            y="20"
            width="120"
            height="40"
          />

          {/* Área grande (inferior) */}
          <rect
            x={width / 2 - 100}
            y={height - 100}
            width="200"
            height="80"
          />

          {/* Área pequena (inferior) */}
          <rect
            x={width / 2 - 60}
            y={height - 60}
            width="120"
            height="40"
          />
        </g>

        {/* Jogadores */}
        {jogadores.map(({ jogador, coordenada_x, coordenada_y, posicao_campo }) => {
          // Escalar coordenadas (0-100) para dimensões do SVG
          const x = (coordenada_x / 100) * (width - 80) + 40;
          const y = (coordenada_y / 100) * (height - 80) + 40;

          return (
            <g key={jogador.id_jogador}>
              {/* Círculo de fundo */}
              <circle
                cx={x}
                cy={y}
                r="30"
                fill="white"
                stroke="#1f2937"
                strokeWidth="3"
                opacity="0.95"
              />

              {/* Foto (substituir com <image> se tiver foto_url) */}
              {jogador.foto_url ? (
                <image
                  x={x - 25}
                  y={y - 25}
                  width="50"
                  height="50"
                  href={jogador.foto_url}
                  clipPath={`circle(25px at ${x}px ${y}px)`}
                />
              ) : (
                <text
                  x={x}
                  y={y}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fill="#1f2937"
                  fontSize="12"
                  fontWeight="bold"
                >
                  {jogador.nome.split(' ')[0].substring(0, 3).toUpperCase()}
                </text>
              )}

              {/* Nome do jogador */}
              <text
                x={x}
                y={y + 45}
                textAnchor="middle"
                fill="white"
                fontSize="12"
                fontWeight="bold"
                stroke="#000"
                strokeWidth="0.5"
              >
                {jogador.nome.split(' ')[0]}
              </text>

              {/* Posição */}
              <text
                x={x}
                y={y + 60}
                textAnchor="middle"
                fill="rgba(255,255,255,0.8)"
                fontSize="10"
              >
                {posicao_campo}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Info da formação */}
      <div className="mt-4 text-center text-white font-semibold">
        Formação: {formacao}
      </div>
    </Card>
  );
}
```

---

## Hook Customizado: useJogadores

### `frontend/src/hooks/useJogadores.ts`

```typescript
import { useQuery } from '@tanstack/react-query';
import { getJogadores } from '@/services/jogadores';
import type { JogadorFilters } from '@/types/jogador';

export function useJogadores(filters: JogadorFilters) {
  return useQuery({
    queryKey: ['jogadores', filters],
    queryFn: () => getJogadores(filters),
    keepPreviousData: true,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });
}
```

---

## Service: Jogadores API

### `frontend/src/services/jogadores.ts`

```typescript
import api from './api';
import type { Jogador, JogadorFilters, PaginatedResponse } from '@/types/jogador';

export async function getJogadores(
  filters: JogadorFilters
): Promise<PaginatedResponse<Jogador>> {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      if (Array.isArray(value)) {
        params.append(key, value.join(','));
      } else {
        params.append(key, String(value));
      }
    }
  });

  const { data } = await api.get(`/jogadores?${params.toString()}`);
  return data;
}

export async function getJogador(id: number): Promise<Jogador> {
  const { data } = await api.get(`/jogadores/${id}`);
  return data;
}

export async function getFilterOptions() {
  const { data } = await api.get('/jogadores/filter-options');
  return data;
}
```

---

Esses componentes fornecem uma base sólida e moderna para a migração do Streamlit para React, mantendo todas as funcionalidades principais e melhorando a experiência do usuário com uma interface responsiva e interativa.
