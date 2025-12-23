/**
 * Layout Component - Scout Pro
 * Layout principal com Sidebar responsiva
 */
import { useState } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import {
  Home,
  Users,
  Star,
  FileText,
  GitCompare,
  Shield,
  TrendingUp,
  Settings as SettingsIcon,
  Menu,
  X,
  LogOut,
  User,
} from "lucide-react";
import { useAuthStore } from "../../store/authStore";
import { Button } from "../ui/Button";
import { cn } from "../../lib/utils";

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Jogadores", href: "/jogadores", icon: Users },
  { name: "Avaliações", href: "/avaliacoes", icon: FileText },
  { name: "Wishlist", href: "/wishlist", icon: Star },
  { name: "Comparador", href: "/comparador", icon: GitCompare },
  { name: "Shadow Team", href: "/shadow-team", icon: Shield },
  { name: "Analytics", href: "/analytics", icon: TrendingUp },
  { name: "Configurações", href: "/settings", icon: SettingsIcon },
];

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-gray-900/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transition-transform duration-300 lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Users className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl text-gray-900">Scout Pro</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-blue-50 text-blue-600"
                    : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                )
              }
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-gray-200 p-2 rounded-full">
              <User className="h-4 w-4 text-gray-600" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-gray-900 truncate">
                {user?.nome || user?.username}
              </div>
              <div className="text-xs text-gray-500 capitalize">
                {user?.nivel}
              </div>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={handleLogout}
          >
            <LogOut className="h-4 w-4 mr-2" />
            Sair
          </Button>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar (mobile) */}
        <header className="sticky top-0 z-30 bg-white border-b border-gray-200 lg:hidden">
          <div className="flex items-center justify-between h-16 px-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-600 hover:text-gray-900"
            >
              <Menu className="h-6 w-6" />
            </button>
            <span className="font-bold text-lg text-gray-900">Scout Pro</span>
            <div className="w-6" /> {/* Spacer for alignment */}
          </div>
        </header>

        {/* Page content */}
        <main className="min-h-[calc(100vh-4rem)] lg:min-h-screen">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
