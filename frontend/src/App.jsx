import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/auth/LoginPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import LibrosPage from './pages/libros/LibrosPage';
import UsuariosPage from './pages/admin/UsuariosPage';
import AuditoriaPage from './pages/admin/AuditoriaPage';
import ProfilePage from './pages/perfil/ProfilePage';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="d-flex justify-content-center p-5"><div className="spinner-border text-primary" /></div>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function AdminRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="d-flex justify-content-center p-5"><div className="spinner-border text-primary" /></div>;
  if (!user) return <Navigate to="/login" replace />;
  if (user.rol !== 'admin') return <Navigate to="/" replace />;
  return children;
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<DashboardPage />} />
        <Route path="libros" element={<LibrosPage />} />
        <Route path="movimientos" element={<Navigate to="/libros" replace />} />
        <Route path="usuarios" element={<AdminRoute><UsuariosPage /></AdminRoute>} />
        <Route path="auditoria" element={<AdminRoute><AuditoriaPage /></AdminRoute>} />
        <Route path="perfil" element={<ProfilePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
