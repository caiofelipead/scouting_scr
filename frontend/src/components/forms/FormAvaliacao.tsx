/**
 * FormAvaliacao Component - Player Evaluation Form
 * 5-dimension evaluation with React Hook Form + Zod
 */
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Save, Loader2, X } from "lucide-react";
import { useCreateAvaliacao, useUpdateAvaliacao } from "../../hooks/useAvaliacoes";
import { Button } from "../ui/Button";
import { Label } from "../ui/Label";
import Slider from "../ui/Slider";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/Card";
import type { Avaliacao } from "../../types";

// Zod Schema for Validation
const avaliacaoSchema = z.object({
  id_jogador: z.number().int().positive("ID do jogador é obrigatório"),
  nota_potencial: z
    .number()
    .min(1, "Nota mínima: 1")
    .max(5, "Nota máxima: 5"),
  nota_tatico: z
    .number()
    .min(1, "Nota mínima: 1")
    .max(5, "Nota máxima: 5"),
  nota_tecnico: z
    .number()
    .min(1, "Nota mínima: 1")
    .max(5, "Nota máxima: 5"),
  nota_fisico: z
    .number()
    .min(1, "Nota mínima: 1")
    .max(5, "Nota máxima: 5"),
  nota_mental: z
    .number()
    .min(1, "Nota mínima: 1")
    .max(5, "Nota máxima: 5"),
  observacoes: z.string().optional(),
});

type AvaliacaoFormData = z.infer<typeof avaliacaoSchema>;

interface FormAvaliacaoProps {
  /** ID do jogador sendo avaliado */
  jogadorId: number;
  /** Nome do jogador (para exibição) */
  jogadorNome?: string;
  /** Avaliação existente (para modo edição) */
  avaliacao?: Avaliacao;
  /** Callback ao salvar com sucesso */
  onSuccess?: () => void;
  /** Callback ao cancelar */
  onCancel?: () => void;
}

/**
 * Formulário de Avaliação Multidimensional
 * - 5 dimensões com sliders visuais (1-5)
 * - Validação com Zod
 * - Integração com React Query
 * - Auto-invalidação do RadarChart após salvar
 *
 * @example
 * <FormAvaliacao
 *   jogadorId={123}
 *   jogadorNome="Neymar Jr"
 *   onSuccess={() => setShowForm(false)}
 *   onCancel={() => setShowForm(false)}
 * />
 */
export default function FormAvaliacao({
  jogadorId,
  jogadorNome,
  avaliacao,
  onSuccess,
  onCancel,
}: FormAvaliacaoProps) {
  const isEditMode = !!avaliacao;

  // Mutations
  const createMutation = useCreateAvaliacao(jogadorId);
  const updateMutation = useUpdateAvaliacao(
    avaliacao?.id_avaliacao || 0,
    jogadorId
  );

  const mutation = isEditMode ? updateMutation : createMutation;

  // React Hook Form
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<AvaliacaoFormData>({
    resolver: zodResolver(avaliacaoSchema),
    defaultValues: {
      id_jogador: jogadorId,
      nota_potencial: avaliacao?.nota_potencial || 3,
      nota_tatico: avaliacao?.nota_tatico || 3,
      nota_tecnico: avaliacao?.nota_tecnico || 3,
      nota_fisico: avaliacao?.nota_fisico || 3,
      nota_mental: avaliacao?.nota_mental || 3,
      observacoes: avaliacao?.observacoes || "",
    },
  });

  // Submit Handler
  const onSubmit = async (data: AvaliacaoFormData) => {
    try {
      await mutation.mutateAsync(data);
      reset();
      onSuccess?.();
    } catch (error) {
      // Error handled by mutation hook (toast)
      console.error("Erro ao salvar avaliação:", error);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>
              {isEditMode ? "Editar Avaliação" : "Nova Avaliação"}
            </CardTitle>
            {jogadorNome && (
              <p className="text-sm text-gray-600 mt-1">
                Jogador: <span className="font-semibold">{jogadorNome}</span>
              </p>
            )}
          </div>
          {onCancel && (
            <Button variant="ghost" size="sm" onClick={onCancel}>
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Potencial */}
          <div>
            <Controller
              name="nota_potencial"
              control={control}
              render={({ field }) => (
                <Slider
                  label="Potencial"
                  value={field.value}
                  onChange={field.onChange}
                  min={1}
                  max={5}
                  step={0.5}
                  showValue
                />
              )}
            />
            {errors.nota_potencial && (
              <p className="text-sm text-red-600 mt-1">
                {errors.nota_potencial.message}
              </p>
            )}
          </div>

          {/* Tático */}
          <div>
            <Controller
              name="nota_tatico"
              control={control}
              render={({ field }) => (
                <Slider
                  label="Tático"
                  value={field.value}
                  onChange={field.onChange}
                  min={1}
                  max={5}
                  step={0.5}
                  showValue
                />
              )}
            />
            {errors.nota_tatico && (
              <p className="text-sm text-red-600 mt-1">
                {errors.nota_tatico.message}
              </p>
            )}
          </div>

          {/* Técnico */}
          <div>
            <Controller
              name="nota_tecnico"
              control={control}
              render={({ field }) => (
                <Slider
                  label="Técnico"
                  value={field.value}
                  onChange={field.onChange}
                  min={1}
                  max={5}
                  step={0.5}
                  showValue
                />
              )}
            />
            {errors.nota_tecnico && (
              <p className="text-sm text-red-600 mt-1">
                {errors.nota_tecnico.message}
              </p>
            )}
          </div>

          {/* Físico */}
          <div>
            <Controller
              name="nota_fisico"
              control={control}
              render={({ field }) => (
                <Slider
                  label="Físico"
                  value={field.value}
                  onChange={field.onChange}
                  min={1}
                  max={5}
                  step={0.5}
                  showValue
                />
              )}
            />
            {errors.nota_fisico && (
              <p className="text-sm text-red-600 mt-1">
                {errors.nota_fisico.message}
              </p>
            )}
          </div>

          {/* Mental */}
          <div>
            <Controller
              name="nota_mental"
              control={control}
              render={({ field }) => (
                <Slider
                  label="Mental"
                  value={field.value}
                  onChange={field.onChange}
                  min={1}
                  max={5}
                  step={0.5}
                  showValue
                />
              )}
            />
            {errors.nota_mental && (
              <p className="text-sm text-red-600 mt-1">
                {errors.nota_mental.message}
              </p>
            )}
          </div>

          {/* Observações */}
          <div>
            <Label htmlFor="observacoes">Observações (opcional)</Label>
            <Controller
              name="observacoes"
              control={control}
              render={({ field }) => (
                <textarea
                  id="observacoes"
                  {...field}
                  rows={4}
                  className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  placeholder="Observações sobre o desempenho do jogador..."
                />
              )}
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isSubmitting}
              >
                Cancelar
              </Button>
            )}
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Salvando...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {isEditMode ? "Atualizar" : "Salvar"} Avaliação
                </>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
