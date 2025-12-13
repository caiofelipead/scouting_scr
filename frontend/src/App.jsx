import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './contexts/authStore'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Jogadores from './pages/Jogadores'
import Avaliacoes from './pages/Avaliacoes'
import Wishlist from './pages/Wishlist'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Routes>
      <Route path="/login" element={
        isAuthenticated ? <Navigate to="/" replace /> : <Login />
      } />

      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<Dashboard />} />
        <Route path="jogadores" element={<Jogadores />} />
        <Route path="avaliacoes" element={<Avaliacoes />} />
        <Route path="wishlist" element={<Wishlist />} />
      </Route>
    </Routes>
  )
}

export default App
