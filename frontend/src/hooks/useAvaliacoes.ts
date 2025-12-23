/**
 * Custom Hook - useAvaliacoes
 * Manage player evaluations with React Query
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import type { AvaliacaoCreate } from "../types";
import * as avaliacoesApi from "../api/avaliacoes";

// Query Keys
export const avaliacoesKeys = {
  all: ["avaliacoes"] as const,
  lists: () => [...avaliacoesKeys.all, "list"] as const,
  list: (jogadorId: number) => [...avaliacoesKeys.lists(), jogadorId] as const,
  details: () => [...avaliacoesKeys.all, "detail"] as const,
  detail: (id: number) => [...avaliacoesKeys.details(), id] as const,
  media: (jogadorId: number) => [...avaliacoesKeys.all, "media", jogadorId] as const,
};

/**
 * Hook para listar avaliações de um jogador
 */
export function useAvaliacoes(jogadorId: number, params?: { page?: number; limit?: number }) {
  return useQuery({
    queryKey: avaliacoesKeys.list(jogadorId),
    queryFn: () => avaliacoesApi.getAvaliacoes(jogadorId, params),
    enabled: !!jogadorId,
    staleTime: 3 * 60 * 1000, // 3 minutos
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para buscar uma avaliação específica
 */
export function useAvaliacao(avaliacaoId: number) {
  return useQuery({
    queryKey: avaliacoesKeys.detail(avaliacaoId),
    queryFn: () => avaliacoesApi.getAvaliacao(avaliacaoId),
    enabled: !!avaliacaoId,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para buscar média das avaliações
 */
export function useMediaAvaliacoes(jogadorId: number) {
  return useQuery({
    queryKey: avaliacoesKeys.media(jogadorId),
    queryFn: () => avaliacoesApi.getMediaAvaliacoes(jogadorId),
    enabled: !!jogadorId,
    staleTime: 2 * 60 * 1000, // 2 minutos
    gcTime: 10 * 60 * 1000,
  });
}

/**
 * Hook para criar avaliação com invalidação automática
 */
export function useCreateAvaliacao(jogadorId?: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: avaliacoesApi.createAvaliacao,
    onSuccess: (data) => {
      // Invalida lista de avaliações do jogador
      if (jogadorId) {
        queryClient.invalidateQueries({ queryKey: avaliacoesKeys.list(jogadorId) });
        queryClient.invalidateQueries({ queryKey: avaliacoesKeys.media(jogadorId) });
      }

      // Invalida todas as listas de jogadores (para atualizar médias)
      queryClient.invalidateQueries({ queryKey: ["jogadores"] });

      toast.success("Avaliação salva com sucesso!", {
        description: `ID: ${data.id_avaliacao}`,
      });
    },
    onError: (error: any) => {
      toast.error("Erro ao salvar avaliação", {
        description: error?.response?.data?.detail || "Tente novamente",
      });
    },
  });
}

/**
 * Hook para atualizar avaliação
 */
export function useUpdateAvaliacao(avaliacaoId: number, jogadorId?: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<AvaliacaoCreate>) =>
      avaliacoesApi.updateAvaliacao(avaliacaoId, data),
    onSuccess: () => {
      // Invalida a avaliação específica
      queryClient.invalidateQueries({ queryKey: avaliacoesKeys.detail(avaliacaoId) });

      // Invalida lista de avaliações do jogador
      if (jogadorId) {
        queryClient.invalidateQueries({ queryKey: avaliacoesKeys.list(jogadorId) });
        queryClient.invalidateQueries({ queryKey: avaliacoesKeys.media(jogadorId) });
      }

      // Invalida listas de jogadores
      queryClient.invalidateQueries({ queryKey: ["jogadores"] });

      toast.success("Avaliação atualizada com sucesso!");
    },
    onError: (error: any) => {
      toast.error("Erro ao atualizar avaliação", {
        description: error?.response?.data?.detail || "Tente novamente",
      });
    },
  });
}

/**
 * Hook para deletar avaliação
 */
export function useDeleteAvaliacao(jogadorId?: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: avaliacoesApi.deleteAvaliacao,
    onSuccess: () => {
      if (jogadorId) {
        queryClient.invalidateQueries({ queryKey: avaliacoesKeys.list(jogadorId) });
        queryClient.invalidateQueries({ queryKey: avaliacoesKeys.media(jogadorId) });
      }
      queryClient.invalidateQueries({ queryKey: ["jogadores"] });

      toast.success("Avaliação removida com sucesso!");
    },
    onError: (error: any) => {
      toast.error("Erro ao remover avaliação", {
        description: error?.response?.data?.detail || "Tente novamente",
      });
    },
  });
}
