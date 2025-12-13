/**
 * Zustand Store - Gerenciamento de estado de autenticação
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authAPI } from '../services/api'

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,

      // Login
      login: async (credentials) => {
        try {
          const response = await authAPI.login(credentials)
          const { access_token, usuario } = response.data

          // Salvar no localStorage
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('user', JSON.stringify(usuario))

          set({
            user: usuario,
            accessToken: access_token,
            isAuthenticated: true,
          })

          return { success: true }
        } catch (error) {
          console.error('Erro no login:', error)
          return {
            success: false,
            error: error.response?.data?.detail || 'Erro ao fazer login',
          }
        }
      },

      // Logout
      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')

        set({
          user: null,
          accessToken: null,
          isAuthenticated: false,
        })
      },

      // Restaurar sessão do localStorage
      restoreSession: () => {
        const token = localStorage.getItem('access_token')
        const userStr = localStorage.getItem('user')

        if (token && userStr) {
          try {
            const user = JSON.parse(userStr)
            set({
              user,
              accessToken: token,
              isAuthenticated: true,
            })
          } catch (error) {
            console.error('Erro ao restaurar sessão:', error)
          }
        }
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)
