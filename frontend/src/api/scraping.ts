/**
 * API Service - Scraping & Sync
 * Web scraping control and Google Sheets synchronization
 */
import api from "../lib/axios";

/**
 * Status de uma tarefa de scraping
 */
export interface ScrapingStatus {
  task_id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number; // 0-100
  current_step?: string;
  total_items?: number;
  processed_items?: number;
  errors?: string[];
  started_at?: string;
  completed_at?: string;
}

/**
 * Resultado da sincronização
 */
export interface SyncResult {
  success: boolean;
  message: string;
  records_created?: number;
  records_updated?: number;
  records_failed?: number;
  total_records?: number;
  errors?: string[];
}

/**
 * Inicia scraping de fotos do Transfermarkt
 */
export async function startPhotoScraping(): Promise<{ task_id: string }> {
  const { data } = await api.post<{ task_id: string }>("/scraping/photos/start");
  return data;
}

/**
 * Inicia scraping de dados gerais (nomes, clubes, etc.)
 */
export async function startDataScraping(): Promise<{ task_id: string }> {
  const { data } = await api.post<{ task_id: string }>("/scraping/data/start");
  return data;
}

/**
 * Busca status de uma tarefa de scraping
 */
export async function getScrapingStatus(taskId: string): Promise<ScrapingStatus> {
  const { data } = await api.get<ScrapingStatus>(`/scraping/status/${taskId}`);
  return data;
}

/**
 * Cancela tarefa de scraping em andamento
 */
export async function cancelScraping(taskId: string): Promise<void> {
  await api.post(`/scraping/cancel/${taskId}`);
}

/**
 * Sincroniza jogadores do Google Sheets
 */
export async function syncGoogleSheets(): Promise<SyncResult> {
  const { data } = await api.post<SyncResult>("/sync/google-sheets");
  return data;
}

/**
 * Exporta jogadores para Google Sheets
 */
export async function exportToGoogleSheets(): Promise<SyncResult> {
  const { data } = await api.post<SyncResult>("/sync/export-to-sheets");
  return data;
}

/**
 * Busca histórico de sincronizações
 */
export async function getSyncHistory(limit: number = 10): Promise<SyncResult[]> {
  const { data } = await api.get<SyncResult[]>("/sync/history", {
    params: { limit },
  });
  return data;
}
