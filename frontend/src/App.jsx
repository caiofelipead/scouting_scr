import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Jogadores from './pages/Jogadores'
import Avaliacoes from './pages/Avaliacoes'
import Wishlist from './pages/Wishlist'
import Comparador from './pages/Comparador'
import ShadowTeam from './pages/ShadowTeam'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'

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
        <Route path="comparador" element={<Comparador />} />
        <Route path="shadow-team" element={<ShadowTeam />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

export default App
