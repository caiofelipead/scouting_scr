/**
 * Custom Hook - useScraping
 * Manage scraping tasks with polling for status updates
 */
import { useState, useEffect, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import * as scrapingApi from "../api/scraping";
import type { ScrapingStatus } from "../api/scraping";

interface UseScrapingOptions {
  /** Intervalo de polling em ms (default: 2000) */
  pollingInterval?: number;
  /** Auto-start polling após iniciar scraping */
  autoStartPolling?: boolean;
}

/**
 * Hook para gerenciar scraping com polling de status
 *
 * @example
 * const { startPhotoScraping, status, isRunning, progress } = useScraping();
 *
 * // Iniciar scraping
 * await startPhotoScraping();
 *
 * // Status atualiza automaticamente via polling
 * console.log(progress); // 0-100
 */
export function useScraping(options: UseScrapingOptions = {}) {
  const { pollingInterval = 2000, autoStartPolling = true } = options;

  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<ScrapingStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  // Derived states
  const isRunning = status?.status === "running" || status?.status === "pending";
  const isCompleted = status?.status === "completed";
  const isFailed = status?.status === "failed";
  const progress = status?.progress || 0;

  /**
   * Polling de status
   */
  const pollStatus = useCallback(async (currentTaskId: string) => {
    try {
      const statusData = await scrapingApi.getScrapingStatus(currentTaskId);
      setStatus(statusData);

      // Para polling se completou ou falhou
      if (statusData.status === "completed") {
        setIsPolling(false);
        toast.success("Scraping concluído!", {
          description: `${statusData.processed_items} itens processados`,
        });
      } else if (statusData.status === "failed") {
        setIsPolling(false);
        toast.error("Scraping falhou", {
          description: statusData.errors?.[0] || "Erro desconhecido",
        });
      }
    } catch (error) {
      console.error("Erro ao buscar status:", error);
      // Continua polling mesmo com erro (pode ser temporário)
    }
  }, []);

  /**
   * Effect para polling automático
   */
  useEffect(() => {
    if (!isPolling || !taskId) return;

    const interval = setInterval(() => {
      pollStatus(taskId);
    }, pollingInterval);

    // Poll imediato
    pollStatus(taskId);

    return () => clearInterval(interval);
  }, [isPolling, taskId, pollingInterval, pollStatus]);

  /**
   * Mutation para iniciar scraping de fotos
   */
  const photoScrapingMutation = useMutation({
    mutationFn: scrapingApi.startPhotoScraping,
    onSuccess: (data) => {
      setTaskId(data.task_id);
      if (autoStartPolling) {
        setIsPolling(true);
      }
      toast.info("Scraping de fotos iniciado", {
        description: `Task ID: ${data.task_id}`,
      });
    },
    onError: (error: any) => {
      toast.error("Erro ao iniciar scraping", {
        description: error?.response?.data?.detail || "Tente novamente",
      });
    },
  });

  /**
   * Mutation para iniciar scraping de dados
   */
  const dataScrapingMutation = useMutation({
    mutationFn: scrapingApi.startDataScraping,
    onSuccess: (data) => {
      setTaskId(data.task_id);
      if (autoStartPolling) {
        setIsPolling(true);
      }
      toast.info("Scraping de dados iniciado", {
        description: `Task ID: ${data.task_id}`,
      });
    },
    onError: (error: any) => {
      toast.error("Erro ao iniciar scraping", {
        description: error?.response?.data?.detail || "Tente novamente",
      });
    },
  });

  /**
   * Mutation para cancelar scraping
   */
  const cancelMutation = useMutation({
    mutationFn: (id: string) => scrapingApi.cancelScraping(id),
    onSuccess: () => {
      setIsPolling(false);
      setStatus(null);
      setTaskId(null);
      toast.warning("Scraping cancelado");
    },
    onError: (error: any) => {
      toast.error("Erro ao cancelar scraping", {
        description: error?.response?.data?.detail || "Tente novamente",
      });
    },
  });

  /**
   * Mutation para sincronizar Google Sheets
   */
  const syncSheetsMutation = useMutation({
    mutationFn: scrapingApi.syncGoogleSheets,
    onSuccess: (result) => {
      if (result.success) {
        toast.success("Sincronização concluída!", {
          description: `${result.records_created || 0} criados, ${
            result.records_updated || 0
          } atualizados`,
        });
      } else {
        toast.error("Sincronização falhou", {
          description: result.message,
        });
      }
    },
    onError: (error: any) => {
      toast.error("Erro na sincronização", {
        description: error?.response?.data?.detail || "Tente novamente",
      });
    },
  });

  return {
    // Actions
    startPhotoScraping: photoScrapingMutation.mutateAsync,
    startDataScraping: dataScrapingMutation.mutateAsync,
    cancelScraping: () => taskId && cancelMutation.mutate(taskId),
    syncGoogleSheets: syncSheetsMutation.mutateAsync,

    // State
    taskId,
    status,
    isRunning,
    isCompleted,
    isFailed,
    progress,
    isPolling,

    // Loading states
    isStarting:
      photoScrapingMutation.isPending || dataScrapingMutation.isPending,
    isSyncing: syncSheetsMutation.isPending,

    // Manual controls
    startPolling: () => setIsPolling(true),
    stopPolling: () => setIsPolling(false),
  };
}
