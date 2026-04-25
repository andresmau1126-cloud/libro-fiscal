import { useEffect, useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { authUpdateMe } from '../../services/api';

export default function ProfilePage() {
  const { user, updateUser } = useAuth();
  const [activeTab, setActiveTab] = useState('info');

  const initials = (user?.nombre || 'U')
    .split(' ')
    .map(w => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  const memberSince = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' })
    : 'N/A';

  return (
    <div className="profile-page">
      {/* ═══════ Hero Header ═══════ */}
      <div className="profile-hero">
        <div className="profile-hero-bg" />
        <div className="profile-hero-content">
          <div className="profile-avatar-ring">
            <div className="profile-avatar">
              {initials}
            </div>
            <div className="profile-avatar-status" />
          </div>
          <div className="profile-hero-info">
            <h1 className="profile-hero-name">{user?.nombre || 'Usuario'}</h1>
            <div className="profile-hero-meta">
              <span className="profile-hero-email">
                <i className="bi bi-envelope-fill" /> {user?.email}
              </span>
              <span className={`profile-role-badge ${user?.rol === 'admin' ? 'role-admin' : 'role-user'}`}>
                <i className={`bi ${user?.rol === 'admin' ? 'bi-shield-fill-check' : 'bi-person-fill'}`} />
                {user?.rol === 'admin' ? 'Administrador' : 'Usuario'}
              </span>
            </div>
          </div>
        </div>
        {/* Decorative elements */}
        <div className="profile-hero-shape shape-1" />
        <div className="profile-hero-shape shape-2" />
        <div className="profile-hero-shape shape-3" />
      </div>

      {/* ═══════ Stats Bar ═══════ */}
      <div className="profile-stats-bar">
        <div className="profile-stat">
          <div className="profile-stat-icon"><i className="bi bi-calendar3" /></div>
          <div>
            <div className="profile-stat-label">Miembro desde</div>
            <div className="profile-stat-value">{memberSince}</div>
          </div>
        </div>
        <div className="profile-stat-divider" />
        <div className="profile-stat">
          <div className="profile-stat-icon"><i className="bi bi-shield-check" /></div>
          <div>
            <div className="profile-stat-label">Rol del sistema</div>
            <div className="profile-stat-value">{user?.rol === 'admin' ? 'Administrador' : 'Usuario estándar'}</div>
          </div>
        </div>
        <div className="profile-stat-divider" />
        <div className="profile-stat">
          <div className="profile-stat-icon"><i className="bi bi-check-circle" /></div>
          <div>
            <div className="profile-stat-label">Estado</div>
            <div className="profile-stat-value">
              <span className="profile-active-dot" /> Activo
            </div>
          </div>
        </div>
      </div>

      {/* ═══════ Content Tabs ═══════ */}
      <div className="profile-tabs">
        <button
          className={`profile-tab ${activeTab === 'info' ? 'active' : ''}`}
          onClick={() => setActiveTab('info')}
        >
          <i className="bi bi-person-lines-fill" /> Información Personal
        </button>
        <button
          className={`profile-tab ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          <i className="bi bi-lock-fill" /> Seguridad
        </button>
        <button
          className={`profile-tab ${activeTab === 'preferences' ? 'active' : ''}`}
          onClick={() => setActiveTab('preferences')}
        >
          <i className="bi bi-gear-fill" /> Preferencias
        </button>
      </div>

      <div className="profile-tab-content">
        {activeTab === 'info' && <InfoTab user={user} />}
        {activeTab === 'security' && <SecurityTab />}
        {activeTab === 'preferences' && <PreferencesTab user={user} updateUser={updateUser} />}
      </div>
    </div>
  );
}

/* ── Info Tab ── */
function InfoTab({ user }) {
  return (
    <div className="profile-card">
      <div className="profile-card-header">
        <h3><i className="bi bi-person-vcard me-2" />Datos de la Cuenta</h3>
        <p>Información asociada a tu perfil en el sistema</p>
      </div>
      <div className="profile-card-body">
        <div className="profile-field-grid">
          <div className="profile-field">
            <div className="profile-field-icon"><i className="bi bi-person" /></div>
            <div>
              <label>Nombre completo</label>
              <p>{user?.nombre || '—'}</p>
            </div>
          </div>
          <div className="profile-field">
            <div className="profile-field-icon"><i className="bi bi-envelope" /></div>
            <div>
              <label>Correo electrónico</label>
              <p>{user?.email || '—'}</p>
            </div>
          </div>
          <div className="profile-field">
            <div className="profile-field-icon"><i className="bi bi-award" /></div>
            <div>
              <label>Rol del sistema</label>
              <p>{user?.rol === 'admin' ? 'Administrador' : 'Usuario'}</p>
            </div>
          </div>
          <div className="profile-field">
            <div className="profile-field-icon"><i className="bi bi-patch-check" /></div>
            <div>
              <label>Estado de cuenta</label>
              <p className="text-success fw-semibold"><i className="bi bi-circle-fill me-1" style={{ fontSize: '.5rem', verticalAlign: 'middle' }} />Activa</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Security Tab ── */
function SecurityTab() {
  const [form, setForm] = useState({ current: '', newPass: '', confirm: '' });
  const [msg, setMsg] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (form.newPass !== form.confirm) {
      setMsg({ ok: false, text: 'Las contraseñas no coinciden' });
      return;
    }
    if (form.newPass.length < 6) {
      setMsg({ ok: false, text: 'La nueva contraseña debe tener al menos 6 caracteres' });
      return;
    }
    setMsg({ ok: true, text: 'Funcionalidad próximamente disponible' });
  };

  return (
    <div className="profile-card">
      <div className="profile-card-header">
        <h3><i className="bi bi-shield-lock me-2" />Cambiar Contraseña</h3>
        <p>Actualiza tu contraseña para mantener tu cuenta segura</p>
      </div>
      <div className="profile-card-body">
        {msg && (
          <div className={`alert ${msg.ok ? 'alert-info' : 'alert-danger'}`} style={{ borderRadius: 12 }}>
            {msg.text}
          </div>
        )}
        <form onSubmit={handleSubmit} style={{ maxWidth: 480 }}>
          <div className="mb-3">
            <label className="form-label fw-semibold">Contraseña actual</label>
            <input type="password" className="form-control" value={form.current} onChange={e => setForm({ ...form, current: e.target.value })} required />
          </div>
          <div className="mb-3">
            <label className="form-label fw-semibold">Nueva contraseña</label>
            <input type="password" className="form-control" value={form.newPass} onChange={e => setForm({ ...form, newPass: e.target.value })} required minLength={6} />
          </div>
          <div className="mb-4">
            <label className="form-label fw-semibold">Confirmar nueva contraseña</label>
            <input type="password" className="form-control" value={form.confirm} onChange={e => setForm({ ...form, confirm: e.target.value })} required minLength={6} />
          </div>
          <button type="submit" className="btn btn-primary px-4">
            <i className="bi bi-check-lg me-1" /> Actualizar Contraseña
          </button>
        </form>
      </div>
    </div>
  );
}

/* ── Preferences Tab ── */
function PreferencesTab({ user, updateUser }) {
  const [prefs, setPrefs] = useState({
    emailNotifications: true,
    currency: 'GTQ',
    timezone: 'GMT-6',
  });
  const [msg, setMsg] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const serverPrefs = user?.preferences;
    if (!serverPrefs) return;
    setPrefs({
      emailNotifications: Boolean(serverPrefs.email_notifications),
      currency: serverPrefs.currency || 'GTQ',
      timezone: serverPrefs.timezone || 'GMT-6',
    });
  }, [user]);

  useEffect(() => {
    if (!msg) return undefined;
    const timer = setTimeout(() => setMsg(null), 2500);
    return () => clearTimeout(timer);
  }, [msg]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const data = await authUpdateMe({
        email_notifications: prefs.emailNotifications,
        currency: prefs.currency,
        timezone: prefs.timezone,
      });
      updateUser(data.user);
      setMsg({ ok: true, text: 'Preferencias guardadas correctamente' });
    } catch {
      setMsg({ ok: false, text: 'No se pudieron guardar las preferencias' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="profile-card">
      <div className="profile-card-header">
        <h3><i className="bi bi-sliders me-2" />Preferencias</h3>
        <p>Personaliza tu experiencia en el sistema</p>
      </div>
      <div className="profile-card-body">
        <div className="d-flex justify-content-end mb-3">
          <button type="button" className="btn btn-primary px-4" onClick={handleSave} disabled={saving}>
            <i className="bi bi-check-lg me-1" /> {saving ? 'Guardando...' : 'Guardar preferencias'}
          </button>
        </div>
        {msg && (
          <div className={`alert ${msg.ok ? 'alert-success' : 'alert-danger'}`} style={{ borderRadius: 12 }}>
            {msg.text}
          </div>
        )}
        <div className="profile-pref-grid">
          <div className="profile-pref-item">
            <div>
              <div className="profile-pref-title">Notificaciones por correo</div>
              <div className="profile-pref-desc">Recibir alertas de actividad por email</div>
            </div>
            <div className="form-check form-switch">
              <input
                className="form-check-input"
                type="checkbox"
                role="switch"
                checked={prefs.emailNotifications}
                onChange={(e) => setPrefs(prev => ({ ...prev, emailNotifications: e.target.checked }))}
                style={{ width: 48, height: 24 }}
              />
            </div>
          </div>
          <div className="profile-pref-item">
            <div>
              <div className="profile-pref-title">Formato de moneda</div>
              <div className="profile-pref-desc">Formato de visualización de montos</div>
            </div>
            <select
              className="form-select"
              style={{ width: 200 }}
              value={prefs.currency}
              onChange={(e) => setPrefs(prev => ({ ...prev, currency: e.target.value }))}
            >
              <option value="GTQ">GTQ (Quetzal)</option>
              <option value="USD">USD (Dólar)</option>
              <option value="COP">COP (Peso Col.)</option>
            </select>
          </div>
          <div className="profile-pref-item">
            <div>
              <div className="profile-pref-title">Zona horaria</div>
              <div className="profile-pref-desc">Para fechas y horas del sistema</div>
            </div>
            <select
              className="form-select"
              style={{ width: 200 }}
              value={prefs.timezone}
              onChange={(e) => setPrefs(prev => ({ ...prev, timezone: e.target.value }))}
            >
              <option value="GMT-6">GMT-6 (Guatemala)</option>
              <option value="GMT-5">GMT-5 (Colombia)</option>
              <option value="GMT-4">GMT-4 (Venezuela)</option>
            </select>
          </div>
        </div>
        <div className="mt-4">
          <button type="button" className="btn btn-primary px-4" onClick={handleSave} disabled={saving}>
            <i className="bi bi-check-lg me-1" /> {saving ? 'Guardando...' : 'Guardar preferencias'}
          </button>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleSave}
          disabled={saving}
          style={{
            position: 'fixed',
            right: 16,
            bottom: 16,
            zIndex: 1050,
            borderRadius: 999,
            boxShadow: '0 10px 24px rgba(0,0,0,0.2)',
            padding: '10px 18px',
          }}
        >
          <i className="bi bi-save2 me-1" /> {saving ? 'Guardando...' : 'Guardar'}
        </button>
      </div>
    </div>
  );
}
