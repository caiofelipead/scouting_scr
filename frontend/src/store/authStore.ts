/**
 * Auth Store - Zustand
 * Gerenciamento de estado de autenticação
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Usuario, Token } from "../types";
import api from "../lib/axios";

interface AuthState {
  // Estado
  user: Usuario | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Ações
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  setUser: (user: Usuario) => void;
  setToken: (token: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Estado inicial
      user: null,
      token: localStorage.getItem("token"),
      isAuthenticated: !!localStorage.getItem("token"),
      isLoading: false,

      // ============================================
      // LOGIN
      // ============================================
      login: async (username: string, password: string) => {
        set({ isLoading: true });

        try {
          const { data } = await api.post<Token>("/auth/login", {
            username,
            password,
          });

          // Salvar token no localStorage
          localStorage.setItem("token", data.access_token);
          if (data.refresh_token) {
            localStorage.setItem("refreshToken", data.refresh_token);
          }

          // Atualizar estado
          set({
            user: data.usuario,
            token: data.access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      // ============================================
      // LOGOUT
      // ============================================
      logout: () => {
        // Limpar localStorage
        localStorage.removeItem("token");
        localStorage.removeItem("refreshToken");

        // Resetar estado
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });

        // Redirecionar para login
        window.location.href = "/login";
      },

      // ============================================
      // REFRESH USER DATA
      // ============================================
      refreshUser: async () => {
        const token = get().token || localStorage.getItem("token");

        if (!token) {
          set({ isAuthenticated: false });
          return;
        }

        try {
          const { data } = await api.get<Usuario>("/auth/me");

          set({
            user: data,
            isAuthenticated: true,
          });
        } catch (error) {
          // Se falhar, fazer logout
          get().logout();
        }
      },

      // ============================================
      // SETTERS
      // ============================================
      setUser: (user: Usuario) => {
        set({ user });
      },

      setToken: (token: string) => {
        localStorage.setItem("token", token);
        set({ token, isAuthenticated: true });
      },
    }),
    {
      name: "auth-storage", // Nome no localStorage
      partialize: (state) => ({
        // Salvar apenas token no localStorage
        // User será recarregado via refreshUser()
        token: state.token,
      }),
    }
  )
);

// Hook para verificar se usuário é admin
export function useIsAdmin(): boolean {
  return useAuthStore((state) => state.user?.nivel === "admin");
}

// Hook para verificar se usuário é coordenador ou admin
export function useIsCoordOrAdmin(): boolean {
  return useAuthStore(
    (state) => state.user?.nivel === "admin" || state.user?.nivel === "coordenador"
  );
}
