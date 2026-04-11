import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';

export default function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
    } catch {
      window.location.href = '/login';
    }
  };

  const closeSidebar = () => setSidebarOpen(false);

  const initials = (user?.nombre || 'U')
    .split(' ')
    .map(w => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="app-layout">
      {/* Mobile toggle */}
      <button className="sidebar-mobile-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
        <i className={`bi ${sidebarOpen ? 'bi-x-lg' : 'bi-list'}`} />
      </button>

      {/* Overlay */}
      {sidebarOpen && <div className="sidebar-overlay" onClick={closeSidebar} />}

      <aside className={`sidebar${sidebarOpen ? ' open' : ''}`}>
        {/* Brand */}
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">
            <i className="bi bi-journal-bookmark-fill" />
          </div>
          <div className="sidebar-brand-text">
            <span className="sidebar-brand-title">Libro Fiscal</span>
            <span className="sidebar-brand-sub">Sistema Contable</span>
          </div>
        </div>

        {/* Navigation */}
        <div className="sidebar-scroll">
          {/* PRINCIPAL */}
          <div className="sidebar-section">
            <div className="sidebar-section-label">Principal</div>
            <ul className="sidebar-nav">
              <li>
                <NavLink to="/" end onClick={closeSidebar}>
                  <i className="bi bi-grid-1x2-fill" />
                  <span>Dashboard</span>
                </NavLink>
              </li>
            </ul>
          </div>

          {/* OPERACIONES */}
          <div className="sidebar-section">
            <div className="sidebar-section-label">Operaciones</div>
            <ul className="sidebar-nav">
              <li>
                <NavLink to="/libros" onClick={closeSidebar}>
                  <i className="bi bi-book-fill" />
                  <span>Libros Fiscales</span>
                </NavLink>
              </li>
            </ul>
          </div>

          {/* ADMINISTRACIÓN (admin only) */}
          {user?.rol === 'admin' && (
            <div className="sidebar-section">
              <div className="sidebar-section-label">Administración</div>
              <ul className="sidebar-nav">
                <li>
                  <NavLink to="/usuarios" onClick={closeSidebar}>
                    <i className="bi bi-people-fill" />
                    <span>Usuarios</span>
                  </NavLink>
                </li>
                <li>
                  <NavLink to="/auditoria" onClick={closeSidebar}>
                    <i className="bi bi-shield-check" />
                    <span>Auditoría</span>
                  </NavLink>
                </li>
              </ul>
            </div>
          )}

          {/* CUENTA */}
          <div className="sidebar-section">
            <div className="sidebar-section-label">Cuenta</div>
            <ul className="sidebar-nav">
              <li>
                <NavLink to="/perfil" onClick={closeSidebar}>
                  <i className="bi bi-person-circle" />
                  <span>Mi Perfil</span>
                </NavLink>
              </li>
            </ul>
          </div>
        </div>

        {/* User card + Logout */}
        <div className="sidebar-footer">
          <NavLink to="/perfil" className="sidebar-user-card" onClick={closeSidebar}>
            <div className="sidebar-user-avatar">{initials}</div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">{user?.nombre}</span>
              <span className="sidebar-user-role">{user?.rol === 'admin' ? 'Administrador' : 'Usuario'}</span>
            </div>
          </NavLink>
          <button className="sidebar-logout-btn" onClick={handleLogout}>
            <i className="bi bi-box-arrow-left" />
          </button>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
