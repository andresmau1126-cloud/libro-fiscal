import { useEffect, useState } from 'react';
import { createProvider, deleteProvider, fetchProviders } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const providerInitial = { nombre: '', nit: '', telefono: '', direccion: '' };

export default function ProvidersPage() {
  const { user } = useAuth();
  const readOnly = user?.rol === 'auditor';
  const [providers, setProviders] = useState([]);
  const [message, setMessage] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(providerInitial);
  const [deleting, setDeleting] = useState(null);

  const load = async () => {
    try {
      const data = await fetchProviders();
      setProviders(data);
    } catch (error) {
      setMessage({ ok: false, text: 'No se pudieron cargar los proveedores.' });
    }
  };

  useEffect(() => { load(); }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage(null);
    try {
      const newProvider = await createProvider({
        nombre: form.nombre.trim(),
        nit: form.nit.trim(),
        telefono: form.telefono.trim(),
        direccion: form.direccion.trim(),
      });
      setProviders([...providers, newProvider]);
      setForm(providerInitial);
      setShowForm(false);
      setMessage({ ok: true, text: 'Proveedor registrado correctamente.' });
    } catch (error) {
      setMessage({ ok: false, text: error.response?.data?.error || 'No se pudo registrar el proveedor.' });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar este proveedor?')) return;
    setDeleting(id);
    setMessage(null);
    try {
      await deleteProvider(id);
      setProviders(providers.filter((p) => p.id !== id));
      setMessage({ ok: true, text: 'Proveedor eliminado correctamente.' });
    } catch (error) {
      setMessage({ ok: false, text: error.response?.data?.error || 'No se pudo eliminar el proveedor.' });
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div className="container-fluid py-3">
      <div className="page-header mb-3">
        <h2><i className="bi bi-building me-2" />Proveedores</h2>
        <p>Gestiona los proveedores de egresos y compras.</p>
      </div>
      {message && <div className={`alert ${message.ok ? 'alert-success' : 'alert-danger'}`}>{message.text}</div>}
      
      {!readOnly && (
        <div className="data-table p-3 mb-3">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5>Agregar Proveedor</h5>
            <button
              type="button"
              className={`btn ${showForm ? 'btn-secondary' : 'btn-primary'}`}
              onClick={() => setShowForm(!showForm)}
            >
              {showForm ? 'Cancelar' : '+ Nuevo'}
            </button>
          </div>
          
          {showForm && (
            <form onSubmit={handleSubmit}>
              <div className="row g-2">
                <div className="col-md-6">
                  <label className="form-label">Nombre del proveedor *</label>
                  <input
                    required
                    maxLength={180}
                    className="form-control"
                    value={form.nombre}
                    onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                    placeholder="Ej: Distribuidora XYZ"
                  />
                </div>
                <div className="col-md-6">
                  <label className="form-label">NIT *</label>
                  <input
                    required
                    maxLength={50}
                    className="form-control"
                    value={form.nit}
                    onChange={(e) => setForm({ ...form, nit: e.target.value })}
                    placeholder="Ej: 900123456-7"
                  />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Teléfono</label>
                  <input
                    maxLength={50}
                    className="form-control"
                    value={form.telefono}
                    onChange={(e) => setForm({ ...form, telefono: e.target.value })}
                    placeholder="Ej: 3001234567"
                  />
                </div>
                <div className="col-md-6">
                  <label className="form-label">Dirección</label>
                  <input
                    maxLength={255}
                    className="form-control"
                    value={form.direccion}
                    onChange={(e) => setForm({ ...form, direccion: e.target.value })}
                    placeholder="Ej: Calle 10 #20-30"
                  />
                </div>
                <div className="col-12 text-end">
                  <button type="submit" className="btn btn-primary">Guardar Proveedor</button>
                </div>
              </div>
            </form>
          )}
        </div>
      )}

      <div className="data-table">
        <div className="table-header">
          <h5>Lista de Proveedores ({providers.length})</h5>
        </div>
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>NIT</th>
                <th>Teléfono</th>
                <th>Dirección</th>
                {!readOnly && <th className="text-center">Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {providers.map((provider) => (
                <tr key={provider.id}>
                  <td>{provider.nombre}</td>
                  <td>{provider.nit || '-'}</td>
                  <td>{provider.telefono || '-'}</td>
                  <td>{provider.direccion || '-'}</td>
                  {!readOnly && (
                    <td className="text-center">
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-danger"
                        onClick={() => handleDelete(provider.id)}
                        disabled={deleting === provider.id}
                        title="Eliminar proveedor"
                      >
                        {deleting === provider.id ? (
                          <span className="spinner-border spinner-border-sm" />
                        ) : (
                          <i className="bi bi-trash" />
                        )}
                      </button>
                    </td>
                  )}
                </tr>
              ))}
              {!providers.length && (
                <tr>
                  <td colSpan={readOnly ? '4' : '5'} className="text-center text-muted py-3">
                    Sin proveedores registrados.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
