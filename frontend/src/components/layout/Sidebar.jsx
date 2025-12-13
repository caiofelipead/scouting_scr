import { NavLink } from 'react-router-dom'

const navigation = [
  { name: 'Dashboard', to: '/' },
  { name: 'Jogadores', to: '/jogadores' },
  { name: 'Avaliações', to: '/avaliacoes' },
  { name: 'Wishlist', to: '/wishlist' },
]

export default function Sidebar() {
  return (
    <div className="bg-primary-900 text-white w-64 p-6">
      <h1 className="text-2xl font-bold mb-8">Scout Pro</h1>

      <nav className="space-y-2">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.to}
            className={({ isActive }) =>
              `block px-4 py-2 rounded ${
                isActive ? 'bg-primary-700' : 'hover:bg-primary-800'
              }`
            }
          >
            {item.name}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
