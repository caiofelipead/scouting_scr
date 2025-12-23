/**
 * Settings Page - Scout Pro
 * Configuration panel with scraping controls and sync
 */
import { useState } from "react";
import {
  Settings as SettingsIcon,
  Download,
  Upload,
  Image,
  Database,
  RefreshCw,
  X,
  CheckCircle,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { useScraping } from "../hooks/useScraping";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import Progress from "../components/ui/Progress";

export default function Settings() {
  const {
    startPhotoScraping,
    startDataScraping,
    syncGoogleSheets,
    cancelScraping,
    status,
    isRunning,
    isCompleted,
    isFailed,
    progress,
    isStarting,
    isSyncing,
    taskId,
  } = useScraping();

  const [activeTab, setActiveTab] = useState<"scraping" | "sync">("scraping");

  /**
   * Handler para scraping de fotos
   */
  const handlePhotoScraping = async () => {
    try {
      await startPhotoScraping();
    } catch (error) {
      console.error("Erro ao iniciar scraping de fotos:", error);
    }
  };

  /**
   * Handler para scraping de dados
   */
  const handleDataScraping = async () => {
    try {
      await startDataScraping();
    } catch (error) {
      console.error("Erro ao iniciar scraping de dados:", error);
    }
  };

  /**
   * Handler para sincronização Google Sheets
   */
  const handleGoogleSheetsSync = async () => {
    try {
      await syncGoogleSheets();
    } catch (error) {
      console.error("Erro ao sincronizar Google Sheets:", error);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="bg-gray-100 p-2 rounded-lg">
              <SettingsIcon className="h-6 w-6 text-gray-700" />
            </div>
            <div>
              <CardTitle className="text-2xl">Configurações</CardTitle>
              <p className="text-sm text-gray-600 mt-1">
                Painel de controle e automação
              </p>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Tabs */}
      <Card>
        <CardContent className="p-0">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab("scraping")}
              className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === "scraping"
                  ? "border-b-2 border-blue-500 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Web Scraping
            </button>
            <button
              onClick={() => setActiveTab("sync")}
              className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === "sync"
                  ? "border-b-2 border-blue-500 text-blue-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Sincronização
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Tab Content: Scraping */}
      {activeTab === "scraping" && (
        <div className="space-y-6">
          {/* Status Card */}
          {taskId && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Status da Tarefa</CardTitle>
                  {isRunning && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => cancelScraping()}
                    >
                      <X className="h-4 w-4 mr-2" />
                      Cancelar
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Task ID */}
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Task ID:</span>
                  <code className="bg-gray-100 px-2 py-1 rounded text-xs">
                    {taskId}
                  </code>
                </div>

                {/* Status Badge */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Status:</span>
                  <StatusBadge
                    status={status?.status || "pending"}
                    isRunning={isRunning}
                    isCompleted={isCompleted}
                    isFailed={isFailed}
                  />
                </div>

                {/* Progress Bar */}
                {isRunning && (
                  <Progress
                    value={progress}
                    showValue
                    variant={
                      progress === 100
                        ? "success"
                        : progress > 50
                        ? "default"
                        : "warning"
                    }
                    size="lg"
                  />
                )}

                {/* Current Step */}
                {status?.current_step && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Etapa atual:</span>{" "}
                    {status.current_step}
                  </div>
                )}

                {/* Items Progress */}
                {status?.total_items && (
                  <div className="text-sm text-gray-600">
                    <span className="font-medium">Progresso:</span>{" "}
                    {status.processed_items || 0} / {status.total_items} itens
                  </div>
                )}

                {/* Errors */}
                {status?.errors && status.errors.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="h-4 w-4 text-red-600 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-red-900 mb-1">
                          Erros encontrados:
                        </p>
                        <ul className="text-xs text-red-700 space-y-1">
                          {status.errors.map((error, i) => (
                            <li key={i}>• {error}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Photo Scraping */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <Image className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <CardTitle>Sincronizar Fotos</CardTitle>
                  <p className="text-sm text-gray-600 mt-1">
                    Baixa fotos do Transfermarkt para jogadores cadastrados
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button
                onClick={handlePhotoScraping}
                disabled={isStarting || isRunning}
                className="w-full"
              >
                {isStarting || isRunning ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {isRunning ? "Executando..." : "Iniciando..."}
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4 mr-2" />
                    Iniciar Scraping de Fotos
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Data Scraping */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="bg-green-100 p-2 rounded-lg">
                  <Database className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <CardTitle>Sincronizar Dados</CardTitle>
                  <p className="text-sm text-gray-600 mt-1">
                    Atualiza informações gerais (nome, clube, idade, etc.)
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button
                onClick={handleDataScraping}
                disabled={isStarting || isRunning}
                className="w-full"
              >
                {isStarting || isRunning ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {isRunning ? "Executando..." : "Iniciando..."}
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4 mr-2" />
                    Iniciar Scraping de Dados
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tab Content: Sync */}
      {activeTab === "sync" && (
        <div className="space-y-6">
          {/* Import from Google Sheets */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="bg-purple-100 p-2 rounded-lg">
                  <Upload className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <CardTitle>Importar do Google Sheets</CardTitle>
                  <p className="text-sm text-gray-600 mt-1">
                    Sincroniza jogadores da planilha para o banco de dados
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Button
                onClick={handleGoogleSheetsSync}
                disabled={isSyncing}
                className="w-full"
              >
                {isSyncing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Sincronizando...
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Sincronizar Agora
                  </>
                )}
              </Button>
              <p className="text-xs text-gray-500 mt-2">
                Esta operação pode levar alguns minutos dependendo do volume de
                dados.
              </p>
            </CardContent>
          </Card>

          {/* Info Card */}
          <Card>
            <CardContent className="py-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-blue-900 mb-1">
                      Sobre a Sincronização
                    </h4>
                    <p className="text-xs text-blue-700">
                      A sincronização com Google Sheets permite manter os dados
                      atualizados entre a planilha e o sistema. Registros novos
                      serão criados e existentes serão atualizados com base no
                      ID do Transfermarkt.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

/**
 * Status Badge Component
 */
function StatusBadge({
  status,
  isRunning,
  isCompleted,
  isFailed,
}: {
  status: string;
  isRunning: boolean;
  isCompleted: boolean;
  isFailed: boolean;
}) {
  if (isRunning) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
        <Loader2 className="h-3 w-3 mr-1 animate-spin" />
        Em Execução
      </span>
    );
  }

  if (isCompleted) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        <CheckCircle className="h-3 w-3 mr-1" />
        Concluído
      </span>
    );
  }

  if (isFailed) {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
        <AlertCircle className="h-3 w-3 mr-1" />
        Falhou
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
      {status}
    </span>
  );
}
