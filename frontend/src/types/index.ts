/**
 * Types TypeScript baseados nos Schemas Pydantic do Backend
 * Referência: backend/app/schemas/
 */

// ============================================
// USUARIO & AUTENTICAÇÃO
// ============================================

export type UserLevel = "admin" | "coordenador" | "scout";

export interface Usuario {
  id: number;
  username: string;
  email: string;
  nome: string | null;
  nivel: UserLevel;
  ativo: boolean;
  data_criacao: string;
  ultimo_acesso: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  nome?: string;
  nivel?: UserLevel;
}

export interface Token {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  usuario: Usuario;
}

// ============================================
// JOGADOR
// ============================================

export interface Jogador {
  id_jogador: number;
  nome: string;
  nacionalidade: string | null;
  ano_nascimento: number | null;
  idade_atual: number | null;
  altura: number | null;
  pe_dominante: string | null;
  transfermarkt_id: string | null;
  data_criacao: string;
  data_atualizacao: string;
}

export interface JogadorWithDetails extends Jogador {
  clube: string | null;
  liga_clube: string | null;
  posicao: string | null;
  status_contrato: string | null;
  data_fim_contrato: string | null;
  em_wishlist: boolean;
  nota_potencial_media: number | null;
  total_avaliacoes: number;
}

export interface JogadorCreate {
  nome: string;
  nacionalidade?: string;
  ano_nascimento?: number;
  idade_atual?: number;
  altura?: number;
  pe_dominante?: string;
  transfermarkt_id?: string;
}

export interface JogadorUpdate {
  nome?: string;
  nacionalidade?: string;
  ano_nascimento?: number;
  idade_atual?: number;
  altura?: number;
  pe_dominante?: string;
  transfermarkt_id?: string;
}

// ============================================
// AVALIAÇÃO
// ============================================

export interface Avaliacao {
  id: number;
  id_jogador: number;
  data_avaliacao: string;
  nota_potencial: number | null;
  nota_tatico: number | null;
  nota_tecnico: number | null;
  nota_fisico: number | null;
  nota_mental: number | null;
  observacoes: string | null;
  avaliador: string | null;
  data_criacao: string;
}

export interface AvaliacaoCreate {
  id_jogador: number;
  data_avaliacao: string;
  nota_potencial?: number;
  nota_tatico?: number;
  nota_tecnico?: number;
  nota_fisico?: number;
  nota_mental?: number;
  observacoes?: string;
  avaliador?: string;
}

export interface AvaliacaoEvolution {
  jogador_id: number;
  evolucao: Array<{
    data_avaliacao: string;
    nota_potencial: number | null;
    nota_tatico: number | null;
    nota_tecnico: number | null;
    nota_fisico: number | null;
    nota_mental: number | null;
    media_geral: number | null;
  }>;
}

// ============================================
// WISHLIST
// ============================================

export type WishlistPriority = "alta" | "media" | "baixa";

export interface Wishlist {
  id_wishlist: number;
  id_jogador: number;
  prioridade: WishlistPriority;
  observacao: string | null;
  adicionado_em: string;
}

export interface WishlistWithJogador extends Wishlist {
  jogador: JogadorWithDetails;
}

export interface WishlistCreate {
  id_jogador: number;
  prioridade: WishlistPriority;
  observacao?: string;
}

export interface WishlistUpdate {
  prioridade?: WishlistPriority;
  observacao?: string;
}

// ============================================
// TAG
// ============================================

export interface Tag {
  id_tag: number;
  nome: string;
  cor: string;
  categoria: string | null;
}

export interface JogadorTag {
  id_jogador: number;
  id_tag: number;
  tag?: Tag;
}

// ============================================
// FILTROS & PAGINAÇÃO
// ============================================

export interface PaginationParams {
  page: number;
  limit: number;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  limit: number;
  pages: number;
  data: T[];
}

export interface JogadorFilters {
  nome?: string;
  posicao?: string;
  clube?: string;
  liga?: string;
  nacionalidade?: string;
  idade_min?: number;
  idade_max?: number;
  media_min?: number;
  page?: number;
  limit?: number;
}

// ============================================
// API RESPONSE
// ============================================

export interface ApiError {
  detail: string;
  status_code?: number;
}

export interface HealthCheck {
  status: string;
  database: string;
  version: string;
}

// ============================================
// VINCULO CLUBE
// ============================================

export interface VinculoClube {
  id_vinculo: number;
  id_jogador: number;
  clube: string;
  liga_clube: string | null;
  posicao: string | null;
  data_inicio_contrato: string | null;
  data_fim_contrato: string | null;
  status_contrato: string | null;
}

// ============================================
// CONSTANTS
// ============================================

export const POSICOES = ["GOL", "LAD", "LAE", "ZAG", "VOL", "MEI", "ATA"] as const;
export type Posicao = typeof POSICOES[number];

export const PRIORIDADES: WishlistPriority[] = ["alta", "media", "baixa"];
export const USER_LEVELS: UserLevel[] = ["admin", "coordenador", "scout"];
