/**
 * Cliente API - Axios configurado para Scout Pro API
 */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Criar instância Axios
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar token JWT em todas as requisições
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ============================================
// AUTENTICAÇÃO
// ============================================

export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  getCurrentUser: () => api.get('/auth/me'),
}

// ============================================
// JOGADORES
// ============================================

export const jogadoresAPI = {
  getAll: (params = {}) => api.get('/jogadores', { params }),
  getById: (id) => api.get(`/jogadores/${id}`),
  create: (data) => api.post('/jogadores', data),
  update: (id, data) => api.put(`/jogadores/${id}`, data),
  delete: (id) => api.delete(`/jogadores/${id}`),
  getStats: () => api.get('/jogadores/stats/total'),
}

// ============================================
// AVALIAÇÕES
// ============================================

export const avaliacoesAPI = {
  getByJogador: (jogadorId, params = {}) =>
    api.get(`/avaliacoes/jogador/${jogadorId}`, { params }),
  getUltima: (jogadorId) =>
    api.get(`/avaliacoes/jogador/${jogadorId}/ultima`),
  create: (data) => api.post('/avaliacoes', data),
  delete: (id) => api.delete(`/avaliacoes/${id}`),
}

// ============================================
// WISHLIST
// ============================================

export const wishlistAPI = {
  getAll: (params = {}) => api.get('/wishlist', { params }),
  add: (data) => api.post('/wishlist', data),
  remove: (jogadorId) => api.delete(`/wishlist/${jogadorId}`),
  check: (jogadorId) => api.get(`/wishlist/check/${jogadorId}`),
}

export default api
