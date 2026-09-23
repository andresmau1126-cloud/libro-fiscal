import { useEffect, useState } from 'react';
import { createCliente, fetchClientes, updateCliente } from '../services/api';

const emptyForm = { nombre: '', nit: '', telefono: '', direccion: '' };

export default function ClientesPage() {
  const [clientes, setClientes] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  const load = async () => {
    setLoading(true);
    try { setClientes(await fetchClientes()); } catch (error) {
      setMessage({ ok: false, text: error.response?.data?.error || 'No se pudieron cargar los clientes.' });
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const submit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const saved = editingId ? await updateCliente(editingId, form) : await createCliente(form);
      await load();
      setForm(emptyForm);
      setEditingId(null);
      setMessage({ ok: true, text: editingId ? 'Cliente actualizado.' : 'Cliente registrado.' });
    } catch (error) {
      setMessage({ ok: false, text: error.response?.data?.error || 'No se pudo guardar el cliente.' });
    } finally { setSaving(false); }
  };

  const edit = (cliente) => {
    setEditingId(cliente.id);
    setForm({ nombre: cliente.nombre, nit: cliente.nit, telefono: cliente.telefono || '', direccion: cliente.direccion || '' });
    setMessage(null);
  };

  return <div className="container-fluid py-3">
    <div className="page-header mb-3"><h2><i className="bi bi-person-vcard me-2" />Registro de clientes</h2><p>Administra clientes y evita duplicar NIT.</p></div>
    {message && <div className={`alert ${message.ok ? 'alert-success' : 'alert-danger'}`}>{message.text}</div>}
    <div className="row g-3">
      <div className="col-lg-4"><div className="data-table p-3"><h5>{editingId ? 'Editar cliente' : 'Nuevo cliente'}</h5><form onSubmit={submit}>
        <label className="form-label">Nombre *</label><input className="form-control mb-2" required value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
        <label className="form-label">NIT *</label><input className="form-control mb-2" required value={form.nit} onChange={(e) => setForm({ ...form, nit: e.target.value })} />
        <label className="form-label">Teléfono</label><input className="form-control mb-2" value={form.telefono} onChange={(e) => setForm({ ...form, telefono: e.target.value })} />
        <label className="form-label">Dirección</label><input className="form-control mb-3" value={form.direccion} onChange={(e) => setForm({ ...form, direccion: e.target.value })} />
        <button className="btn btn-primary" disabled={saving}>{saving ? 'Guardando...' : 'Guardar cliente'}</button>
        {editingId && <button type="button" className="btn btn-link" onClick={() => { setEditingId(null); setForm(emptyForm); }}>Cancelar</button>}
      </form></div></div>
      <div className="col-lg-8"><div className="data-table p-3"><h5>Clientes registrados</h5>{loading ? <div>Cargando...</div> : <div className="table-responsive"><table className="table align-middle"><thead><tr><th>Nombre</th><th>NIT</th><th>Teléfono</th><th /></tr></thead><tbody>{clientes.map((cliente) => <tr key={cliente.id}><td>{cliente.nombre}</td><td>{cliente.nit}</td><td>{cliente.telefono || '-'}</td><td className="text-end"><button className="btn btn-sm btn-outline-primary" onClick={() => edit(cliente)}>Editar</button></td></tr>)}{!clientes.length && <tr><td colSpan="4" className="text-center text-muted">No hay clientes registrados.</td></tr>}</tbody></table></div>}</div></div>
    </div>
  </div>;
}
