import { useEffect, useState } from 'react';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { createProvider, deleteProvider, fetchProviders, updateProvider } from '../../services/api';
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
  const [editingProvider, setEditingProvider] = useState(null);
  const [editForm, setEditForm] = useState({ nit: '', phone: '', address: '' });
  const [savingEdit, setSavingEdit] = useState(false);

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

  const openEdit = (provider) => {
    setEditingProvider(provider);
    setEditForm({ nit: provider.nit || '', phone: provider.telefono || '', address: provider.direccion || '' });
  };

  const handleEditSubmit = async (event) => {
    event.preventDefault();
    if (!/^\d{10}$/.test(editForm.phone)) {
      toast.error('El teléfono debe tener exactamente 10 dígitos.');
      return;
    }

    setSavingEdit(true);
    try {
      const updatedProvider = await updateProvider(editingProvider.id, editForm);
      setProviders((currentProviders) => currentProviders.map((provider) => (
        provider.id === editingProvider.id ? { ...provider, ...updatedProvider } : provider
      )));
      setEditingProvider(null);
      toast.success("Actualizado");
    } catch (error) {
      toast.error(error.response?.data?.error || 'No se pudo actualizar el proveedor.');
    } finally {
      setSavingEdit(false);
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
                        className="btn btn-sm btn-outline-primary me-1"
                        onClick={() => openEdit(provider)}
                        title="Editar proveedor"
                      >
                        <i className="bi bi-pencil" />
                      </button>
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

      {editingProvider && (
        <div className="modal-backdrop-custom" onClick={() => setEditingProvider(null)}>
          <div className="modal-content-custom" onClick={(event) => event.stopPropagation()}>
            <div className="modal-header-custom">
              <h5>Editar proveedor</h5>
              <button type="button" className="btn-close" onClick={() => setEditingProvider(null)} />
            </div>
            <form onSubmit={handleEditSubmit}>
              <div className="modal-body-custom">
                <div className="mb-3">
                  <label className="form-label" htmlFor="provider-nit">NIT / número de proveedor</label>
                  <input
                    id="provider-nit"
                    type="text"
                    className="form-control"
                    value={editForm.nit}
                    onChange={(event) => setEditForm({ ...editForm, nit: event.target.value })}
                    maxLength={50}
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label" htmlFor="provider-phone">Teléfono</label>
                  <input
                    id="provider-phone"
                    type="tel"
                    className="form-control"
                    value={editForm.phone}
                    onChange={(event) => setEditForm({ ...editForm, phone: event.target.value })}
                    inputMode="numeric"
                    maxLength={10}
                    required
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label" htmlFor="provider-address">Dirección</label>
                  <input
                    id="provider-address"
                    type="text"
                    className="form-control"
                    value={editForm.address}
                    onChange={(event) => setEditForm({ ...editForm, address: event.target.value })}
                    maxLength={255}
                  />
                </div>
              </div>
              <div className="modal-footer-custom">
                <button type="button" className="btn btn-light" onClick={() => setEditingProvider(null)}>Cancelar</button>
                <button type="submit" className="btn btn-primary" disabled={savingEdit}>
                  {savingEdit ? 'Guardando...' : 'Guardar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      <ToastContainer position="top-right" autoClose={3000} />
    </div>
  );
}
