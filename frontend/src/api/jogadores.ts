/**
 * API Service - Jogadores
 * Funções para consumo dos endpoints de jogadores
 */
import { api } from "../lib/axios";
import type {
  Jogador,
  JogadorWithDetails,
  JogadorCreate,
  JogadorUpdate,
  PaginatedResponse,
  JogadorFilters,
} from "../types";

/**
 * Lista jogadores com paginação e filtros
 */
export async function getJogadores(
  filters: JogadorFilters = {}
): Promise<PaginatedResponse<JogadorWithDetails>> {
  const { data } = await api.get<PaginatedResponse<JogadorWithDetails>>(
    "/jogadores",
    { params: filters }
  );
  return data;
}

/**
 * Busca jogador por ID
 */
export async function getJogador(
  id: number
): Promise<JogadorWithDetails> {
  const { data } = await api.get<JogadorWithDetails>(`/jogadores/${id}`);
  return data;
}

/**
 * Cria novo jogador
 */
export async function createJogador(
  jogador: JogadorCreate
): Promise<Jogador> {
  const { data } = await api.post<Jogador>("/jogadores", jogador);
  return data;
}

/**
 * Atualiza jogador existente
 */
export async function updateJogador(
  id: number,
  jogador: JogadorUpdate
): Promise<Jogador> {
  const { data } = await api.put<Jogador>(`/jogadores/${id}`, jogador);
  return data;
}

/**
 * Deleta jogador
 */
export async function deleteJogador(id: number): Promise<void> {
  await api.delete(`/jogadores/${id}`);
}

/**
 * Busca jogadores com debounce (para SearchInput)
 */
export async function searchJogadores(
  query: string,
  limit: number = 10
): Promise<JogadorWithDetails[]> {
  const { data } = await api.get<PaginatedResponse<JogadorWithDetails>>(
    "/jogadores",
    {
      params: { nome: query, limit },
    }
  );
  return data.data;
}
