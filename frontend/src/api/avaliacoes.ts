/**
 * API Service - Avaliações
 * CRUD operations for player evaluations
 */
import api from "../lib/axios";
import type {
  Avaliacao,
  AvaliacaoCreate,
  PaginatedResponse,
} from "../types";

/**
 * Lista avaliações de um jogador
 */
export async function getAvaliacoes(
  jogadorId: number,
  params?: { page?: number; limit?: number }
): Promise<PaginatedResponse<Avaliacao>> {
  const { data } = await api.get<PaginatedResponse<Avaliacao>>(
    `/jogadores/${jogadorId}/avaliacoes`,
    { params }
  );
  return data;
}

/**
 * Busca avaliação por ID
 */
export async function getAvaliacao(
  avaliacaoId: number
): Promise<Avaliacao> {
  const { data } = await api.get<Avaliacao>(`/avaliacoes/${avaliacaoId}`);
  return data;
}

/**
 * Cria nova avaliação
 */
export async function createAvaliacao(
  avaliacao: AvaliacaoCreate
): Promise<Avaliacao> {
  const { data } = await api.post<Avaliacao>("/avaliacoes", avaliacao);
  return data;
}

/**
 * Atualiza avaliação existente
 */
export async function updateAvaliacao(
  avaliacaoId: number,
  avaliacao: Partial<AvaliacaoCreate>
): Promise<Avaliacao> {
  const { data } = await api.put<Avaliacao>(
    `/avaliacoes/${avaliacaoId}`,
    avaliacao
  );
  return data;
}

/**
 * Deleta avaliação
 */
export async function deleteAvaliacao(avaliacaoId: number): Promise<void> {
  await api.delete(`/avaliacoes/${avaliacaoId}`);
}

/**
 * Busca média das avaliações de um jogador
 */
export async function getMediaAvaliacoes(
  jogadorId: number
): Promise<{
  potencial: number | null;
  tatico: number | null;
  tecnico: number | null;
  fisico: number | null;
  mental: number | null;
}> {
  const { data } = await api.get(`/jogadores/${jogadorId}/avaliacoes/media`);
  return data;
}
