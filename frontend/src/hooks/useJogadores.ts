/**
 * Custom Hook - useJogadores
 * Gerencia estado e fetching de jogadores com React Query
 */
import { useQuery, useInfiniteQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import type { JogadorFilters, JogadorWithDetails } from "../types";
import * as jogadoresApi from "../api/jogadores";

// Query Keys
export const jogadoresKeys = {
  all: ["jogadores"] as const,
  lists: () => [...jogadoresKeys.all, "list"] as const,
  list: (filters: JogadorFilters) => [...jogadoresKeys.lists(), filters] as const,
  details: () => [...jogadoresKeys.all, "detail"] as const,
  detail: (id: number) => [...jogadoresKeys.details(), id] as const,
};

/**
 * Hook para listar jogadores com paginação e filtros
 *
 * @param filters - Filtros de busca, posição, clube, etc.
 * @returns Query result com data, isLoading, isError, etc.
 *
 * @example
 * const { data, isLoading, isError } = useJogadores({
 *   nome: "Neymar",
 *   posicao: "ATA",
 *   page: 1,
 *   limit: 20
 * });
 */
export function useJogadores(filters: JogadorFilters = {}) {
  return useQuery({
    queryKey: jogadoresKeys.list(filters),
    queryFn: () => jogadoresApi.getJogadores(filters),
    staleTime: 5 * 60 * 1000, // 5 minutos - dados considerados frescos
    gcTime: 10 * 60 * 1000, // 10 minutos - tempo em cache (antes era cacheTime)
    refetchOnWindowFocus: false, // Não refetch ao focar janela
    retry: 2, // Tentar 2 vezes em caso de erro
  });
}

/**
 * Hook para paginação infinita (scroll infinito)
 *
 * @param filters - Filtros de busca
 * @returns Infinite query com fetchNextPage, hasNextPage, etc.
 *
 * @example
 * const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useJogadoresInfinite({
 *   posicao: "ATA"
 * });
 */
export function useJogadoresInfinite(filters: Omit<JogadorFilters, "page"> = {}) {
  return useInfiniteQuery({
    queryKey: jogadoresKeys.list({ ...filters, page: 0 }),
    queryFn: ({ pageParam = 1 }) =>
      jogadoresApi.getJogadores({ ...filters, page: pageParam }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      // Se a página atual é menor que o total de páginas, retorna próxima
      if (lastPage.page < lastPage.pages) {
        return lastPage.page + 1;
      }
      return undefined; // Sem mais páginas
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para buscar jogador por ID
 *
 * @param id - ID do jogador
 * @returns Query result com dados do jogador
 */
export function useJogador(id: number) {
  return useQuery({
    queryKey: jogadoresKeys.detail(id),
    queryFn: () => jogadoresApi.getJogador(id),
    enabled: !!id, // Só executa se ID existir
    staleTime: 10 * 60 * 1000, // 10 minutos para detalhes
    gcTime: 30 * 60 * 1000, // 30 minutos em cache
  });
}

/**
 * Hook para criar jogador (mutation)
 */
export function useCreateJogador() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: jogadoresApi.createJogador,
    onSuccess: () => {
      // Invalida todas as listas de jogadores para refetch
      queryClient.invalidateQueries({ queryKey: jogadoresKeys.lists() });
      toast.success("Jogador criado com sucesso!");
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Erro ao criar jogador");
    },
  });
}

/**
 * Hook para atualizar jogador (mutation)
 */
export function useUpdateJogador(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: any) => jogadoresApi.updateJogador(id, data),
    onSuccess: () => {
      // Invalida listas e o detalhe específico
      queryClient.invalidateQueries({ queryKey: jogadoresKeys.lists() });
      queryClient.invalidateQueries({ queryKey: jogadoresKeys.detail(id) });
      toast.success("Jogador atualizado com sucesso!");
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Erro ao atualizar jogador");
    },
  });
}

/**
 * Hook para deletar jogador (mutation)
 */
export function useDeleteJogador() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: jogadoresApi.deleteJogador,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: jogadoresKeys.lists() });
      toast.success("Jogador removido com sucesso!");
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail || "Erro ao remover jogador");
    },
  });
}
