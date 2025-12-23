/**
 * Login Page - Scout Pro
 * Autenticação com React Hook Form + Zod
 */
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { LogIn, Loader2 } from "lucide-react";

import { useAuthStore } from "../store/authStore";
import { getErrorMessage } from "../lib/axios";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Label } from "../components/ui/Label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/Card";

// Schema de validação com Zod
const loginSchema = z.object({
  username: z
    .string()
    .min(3, "Usuário deve ter no mínimo 3 caracteres")
    .max(100, "Usuário muito longo"),
  password: z
    .string()
    .min(6, "Senha deve ter no mínimo 6 caracteres")
    .max(100, "Senha muito longa"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function Login() {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();

  // React Hook Form com validação Zod
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  // Handler de submit
  const onSubmit = async (data: LoginFormData) => {
    try {
      await login(data.username, data.password);
      toast.success("Login realizado com sucesso!");
      navigate("/");
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message || "Erro ao fazer login");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 to-blue-900 p-4">
      <Card className="w-full max-w-md shadow-2xl">
        <CardHeader className="space-y-1 text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-blue-600 p-3 rounded-full">
              <LogIn className="h-8 w-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold">Scout Pro</CardTitle>
          <CardDescription className="text-base">
            Sistema de Scouting de Jogadores de Futebol
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Campo Username */}
            <div className="space-y-2">
              <Label htmlFor="username">Usuário</Label>
              <Input
                id="username"
                type="text"
                placeholder="Digite seu usuário"
                {...register("username")}
                disabled={isSubmitting || isLoading}
              />
              {errors.username && (
                <p className="text-sm text-red-600">
                  {errors.username.message}
                </p>
              )}
            </div>

            {/* Campo Password */}
            <div className="space-y-2">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                type="password"
                placeholder="Digite sua senha"
                {...register("password")}
                disabled={isSubmitting || isLoading}
              />
              {errors.password && (
                <p className="text-sm text-red-600">
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Botão de Submit */}
            <Button
              type="submit"
              className="w-full"
              size="lg"
              disabled={isSubmitting || isLoading}
            >
              {isSubmitting || isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Entrando...
                </>
              ) : (
                <>
                  <LogIn className="mr-2 h-4 w-4" />
                  Entrar
                </>
              )}
            </Button>
          </form>

          {/* Info adicional */}
          <div className="mt-6 text-center text-sm text-gray-500">
            <p>Entre com suas credenciais de scout</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
