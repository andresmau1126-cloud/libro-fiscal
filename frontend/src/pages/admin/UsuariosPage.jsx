import { useState, useEffect } from 'react';
import { fetchUsuarios, createUsuario, updateUsuario, deleteUsuario } from '../../services/api';

export default function UsuariosPage() {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState({ nombre: '', email: '', password: '', rol: 'usuario' });
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    fetchUsuarios()
      .then(setUsuarios)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const openNew = () => {
    setForm({ nombre: '', email: '', password: '', rol: 'usuario' });
    setEditingId(null);
    setError('');
    setShowModal(true);
  };

  const openEdit = (u) => {
    setForm({ nombre: u.nombre, email: u.email, password: '', rol: u.rol });
    setEditingId(u.id);
    setError('');
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      const payload = { nombre: form.nombre, email: form.email, rol: form.rol };
      if (form.password) payload.password = form.password;

      if (editingId) {
        await updateUsuario(editingId, payload);
      } else {
        payload.password = form.password;
        await createUsuario(payload);
      }
      setShowModal(false);
      load();
    } catch (err) {
      setError(err.response?.data?.error || 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteUser = async (id, nombre) => {
    if (!window.confirm(`¿Eliminar al usuario "${nombre}"? Esta acción borrará su cuenta.`)) return;
    try {
      await deleteUsuario(id);
      load();
    } catch (err) {
      alert(err.response?.data?.error || 'Error al eliminar');
    }
  };

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  return (
    <>
      <div className="page-header d-flex justify-content-between align-items-start">
        <div>
          <h2>Usuarios</h2>
          <p>Gestión de cuentas de usuario</p>
        </div>
        <button className="btn-brand" onClick={openNew}>
          <i className="bi bi-person-plus-fill" /> Nuevo Usuario
        </button>
      </div>

      <div className="data-table">
        <div className="table-header">
          <h5>Listado de Usuarios ({usuarios.length})</h5>
        </div>
        {loading ? (
          <div className="d-flex justify-content-center p-4"><div className="spinner-border text-primary" /></div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Email</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Creado</th>
                <th className="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map(u => (
                <tr key={u.id}>
                  <td className="fw-semibold">{u.nombre}</td>
                  <td>{u.email}</td>
                  <td>
                    <span className={u.rol === 'admin' ? 'badge-admin' : 'badge bg-secondary bg-opacity-10 text-dark'} style={{ borderRadius: 20, padding: '0.2rem 0.6rem', fontSize: '0.75rem' }}>
                      {u.rol}
                    </span>
                  </td>
                  <td>
                    <span className={u.activo ? 'badge-active' : 'badge-inactive'}>
                      {u.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.85rem' }}>{u.created_at?.slice(0, 10)}</td>
                  <td className="text-end">
                    <button className="btn btn-sm btn-outline-primary me-1" onClick={() => openEdit(u)} title="Editar">
                      <i className="bi bi-pencil" />
                    </button>
                    <button className="btn btn-sm btn-outline-danger" onClick={() => handleDeleteUser(u.id, u.nombre)} title="Eliminar usuario">
                      <i className="bi bi-trash" />
                    </button>
                  </td>
                </tr>
              ))}
              {usuarios.length === 0 && (
                <tr><td colSpan={6} className="text-center text-muted py-4">Sin usuarios</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-backdrop-custom" onClick={() => setShowModal(false)}>
          <div className="modal-content-custom" onClick={e => e.stopPropagation()}>
            <div className="modal-header-custom">
              <h5>{editingId ? 'Editar Usuario' : 'Nuevo Usuario'}</h5>
              <button className="btn-close" onClick={() => setShowModal(false)} />
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body-custom">
                {error && <div className="alert alert-danger" style={{ borderRadius: 12 }}>{error}</div>}
                <div className="mb-3">
                  <label className="form-label">Nombre</label>
                  <input type="text" className="form-control" value={form.nombre} onChange={set('nombre')} required minLength={2} maxLength={150} />
                </div>
                <div className="mb-3">
                  <label className="form-label">Email</label>
                  <input type="email" className="form-control" value={form.email} onChange={set('email')} required />
                </div>
                <div className="mb-3">
                  <label className="form-label">Contraseña {editingId && '(dejar vacío para no cambiar)'}</label>
                  <input type="password" className="form-control" value={form.password} onChange={set('password')} minLength={editingId ? 0 : 6} required={!editingId} />
                </div>
                <div className="mb-3">
                  <label className="form-label">Rol</label>
                  <select className="form-select" value={form.rol} onChange={set('rol')}>
                    <option value="usuario">Usuario</option>
                    <option value="admin">Administrador</option>
                  </select>
                </div>
              </div>
              <div className="modal-footer-custom">
                <button type="button" className="btn-outline" onClick={() => setShowModal(false)}>Cancelar</button>
                <button type="submit" className="btn-brand" disabled={saving}>
                  {saving ? 'Guardando...' : 'Guardar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
