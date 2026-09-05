import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/auth/LoginPage';
import DashboardPage from './pages/dashboard/DashboardPage';
import LibrosPage from './pages/libros/LibrosPage';
import InventarioPage from './pages/inventario/InventarioPage';
import VentasPage from './pages/ventas/VentasPage';
import UsuariosPage from './pages/admin/UsuariosPage';
import AuditoriaPage from './pages/admin/AuditoriaPage';
import VentasControlPage from './pages/admin/VentasControlPage';
import ProfilePage from './pages/perfil/ProfilePage';
import Respaldos from './pages/Respaldos';
import ApoyosPage from './pages/apoyos/ApoyosPage';

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

function AuditRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="d-flex justify-content-center p-5"><div className="spinner-border text-primary" /></div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!['admin', 'gerente', 'auditor'].includes(user.rol)) return <Navigate to="/" replace />;
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
        <Route path="inventario" element={<InventarioPage />} />
        <Route path="ventas" element={<VentasPage />} />
        <Route path="apoyos" element={<ApoyosPage />} />
        <Route path="movimientos" element={<Navigate to="/libros" replace />} />
        <Route path="usuarios" element={<AdminRoute><UsuariosPage /></AdminRoute>} />
        <Route path="auditoria" element={<AuditRoute><AuditoriaPage /></AuditRoute>} />
        <Route path="ventas-control" element={<AuditRoute><VentasControlPage /></AuditRoute>} />
        <Route path="respaldos" element={<AdminRoute><Respaldos /></AdminRoute>} />
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
