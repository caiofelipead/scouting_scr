/**
 * Avaliações Page - Scout Pro
 * Listagem e gestão de avaliações de jogadores
 */
import { FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";

export default function Avaliacoes() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Avaliações</CardTitle>
          <p className="text-sm text-gray-600 mt-1">
            Gerenciamento de avaliações de jogadores
          </p>
        </CardHeader>
      </Card>

      {/* Placeholder */}
      <Card>
        <CardContent className="py-16">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
              <FileText className="h-8 w-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Em Desenvolvimento
            </h3>
            <p className="text-gray-600 max-w-md mx-auto">
              Esta página permitirá visualizar, criar e editar avaliações de
              jogadores com as 5 dimensões (Potencial, Tático, Técnico, Físico,
              Mental).
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
