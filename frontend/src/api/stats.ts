/**
 * API Service - Statistics & Dashboard
 * KPIs and analytics endpoints
 */
import api from "../lib/axios";

/**
 * Dashboard stats interface
 */
export interface DashboardStats {
  total_jogadores: number;
  crescimento_semanal: number; // Percentage
  media_geral: number;
  meta_clube: number;
  alertas_contrato: number;
  wishlist_ativa: number;
  distribuicao_posicao: {
    posicao: string;
    count: number;
  }[];
}

/**
 * Top prospect interface
 */
export interface TopProspect {
  id_jogador: number;
  nome: string;
  idade_atual: number;
  posicao: string;
  clube: string;
  media_geral: number;
  transfermarkt_id: number | null;
}

/**
 * Activity feed item interface
 */
export interface ActivityItem {
  id: number;
  tipo: "avaliacao" | "jogador_novo" | "wishlist_add";
  descricao: string;
  usuario: string;
  created_at: string;
  metadata?: any;
}

/**
 * System status interface
 */
export interface SystemStatus {
  api_transfermarkt: "online" | "offline" | "error";
  google_sheets: "online" | "offline" | "error";
  database: "online" | "offline" | "error";
  ultimo_sync: string | null;
}

/**
 * Fetch dashboard statistics
 */
export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await api.get<DashboardStats>("/stats/dashboard");
  return data;
}

/**
 * Fetch top prospects (U23 with highest average)
 */
export async function getTopProspects(
  limit: number = 5
): Promise<TopProspect[]> {
  const { data } = await api.get<TopProspect[]>("/stats/top-prospects", {
    params: { limit },
  });
  return data;
}

/**
 * Fetch recent activity feed
 */
export async function getActivityFeed(
  limit: number = 5
): Promise<ActivityItem[]> {
  const { data } = await api.get<ActivityItem[]>("/stats/activity-feed", {
    params: { limit },
  });
  return data;
}

/**
 * Fetch system status
 */
export async function getSystemStatus(): Promise<SystemStatus> {
  const { data } = await api.get<SystemStatus>("/stats/system-status");
  return data;
}
