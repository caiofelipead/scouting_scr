/**
 * Wishlist Page - Scout Pro
 * Listagem de jogadores na wishlist com priorização
 */
import { Star } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";

export default function Wishlist() {
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Wishlist</CardTitle>
          <p className="text-sm text-gray-600 mt-1">
            Jogadores de interesse com priorização
          </p>
        </CardHeader>
      </Card>

      {/* Placeholder */}
      <Card>
        <CardContent className="py-16">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-100 mb-4">
              <Star className="h-8 w-8 text-yellow-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Em Desenvolvimento
            </h3>
            <p className="text-gray-600 max-w-md mx-auto">
              Esta página permitirá gerenciar jogadores de interesse com
              priorização (Alta, Média, Baixa) e observações específicas.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
