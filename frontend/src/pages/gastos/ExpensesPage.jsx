import { useEffect, useState } from 'react';
import { createExpense, createProvider, fetchExpenses, fetchLibros, fetchProviders } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const initial = { provider: '', descripcion: 'Compra a proveedor', fecha: new Date().toISOString().slice(0, 10), descripcion_producto: '', valor_unitario: '', valor_pagado: '', cantidad: '1', libro: '' };
const providerInitial = { nombre: '', nit: '' };

export default function ExpensesPage() {
  const { user } = useAuth();
  const readOnly = user?.rol === 'auditor';
  const [form, setForm] = useState(initial);
  const [providers, setProviders] = useState([]);
  const [libros, setLibros] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [message, setMessage] = useState(null);
  const [providerForm, setProviderForm] = useState(providerInitial);
  const [showProviderForm, setShowProviderForm] = useState(false);

  const load = async () => {
    const [providerRows, libroRows, expenseRows] = await Promise.all([fetchProviders(), fetchLibros(), fetchExpenses()]);
    setProviders(providerRows); setLibros(libroRows); setExpenses(expenseRows);
    setForm((current) => ({ ...current, provider: current.provider || providerRows[0]?.id || '', libro: current.libro || libroRows[0]?.id || '' }));
  };
  useEffect(() => { load().catch(() => setMessage({ ok: false, text: 'No se pudieron cargar los egresos.' })); }, []);
  const update = (field) => (event) => setForm({ ...form, [field]: event.target.value });
  const submit = async (event) => {
    event.preventDefault(); setMessage(null);
    try {
      const cantidad = Number(form.cantidad);
      const valorPagado = Number(form.valor_pagado);
      await createExpense({ ...form, descripcion: `Compra: ${form.descripcion_producto.trim()}`, provider: Number(form.provider), libro: Number(form.libro), cantidad, valor_pagado: valorPagado, valor_unitario: valorPagado / cantidad });
      setForm({ ...initial, fecha: form.fecha, provider: form.provider, libro: form.libro }); setMessage({ ok: true, text: 'Compra registrada al proveedor.' }); await load();
    }
    catch (error) { setMessage({ ok: false, text: error.response?.data?.error || 'No se pudo registrar el egreso.' }); }
  };
  const addProvider = async (event) => {
    event.preventDefault();
    setMessage(null);
    try {
      const provider = await createProvider({ nombre: providerForm.nombre.trim(), nit: providerForm.nit.trim() });
      setProviders([...providers, provider]);
      setForm({ ...form, provider: provider.id });
      setProviderForm(providerInitial);
      setShowProviderForm(false);
      setMessage({ ok: true, text: 'Proveedor registrado con su NIT.' });
    } catch (error) {
      setMessage({ ok: false, text: error.response?.data?.error || 'No se pudo registrar el proveedor.' });
    }
  };

  return <div className="container-fluid py-3"><div className="page-header mb-3"><h2><i className="bi bi-receipt me-2" />Compras a proveedores</h2><p>Registra rápidamente qué se compró, cuánto se pagó y a qué proveedor.</p></div>{message && <div className={`alert ${message.ok ? 'alert-success' : 'alert-danger'}`}>{message.text}</div>}
    {!readOnly && <div className="data-table p-3 mb-3"><form onSubmit={submit}><div className="row g-2"><div className="col-md-4"><label className="form-label">Proveedor</label><div className="input-group"><select required className="form-select" value={form.provider} onChange={update('provider')}><option value="">Seleccione</option>{providers.map((row) => <option key={row.id} value={row.id}>{row.nombre}{row.nit ? ` (${row.nit})` : ''}</option>)}</select><button type="button" className="btn btn-outline-secondary" onClick={() => setShowProviderForm(!showProviderForm)} title="Nuevo proveedor">+</button></div>{showProviderForm && <div className="border rounded p-2 mt-2"><label className="form-label small">Nombre del proveedor</label><input required maxLength={180} className="form-control mb-2" value={providerForm.nombre} onChange={(event) => setProviderForm({ ...providerForm, nombre: event.target.value })} /><label className="form-label small">NIT</label><input required maxLength={50} className="form-control mb-2" placeholder="Ej: 900123456-7" value={providerForm.nit} onChange={(event) => setProviderForm({ ...providerForm, nit: event.target.value })} /><div className="text-end"><button type="button" className="btn btn-sm btn-light me-2" onClick={() => setShowProviderForm(false)}>Cancelar</button><button type="button" className="btn btn-sm btn-primary" onClick={addProvider}>Guardar proveedor</button></div></div>}</div><div className="col-md-4"><label className="form-label">Qué se compró</label><input required maxLength={255} className="form-control" placeholder="Ej: Papelería" value={form.descripcion_producto} onChange={update('descripcion_producto')} /></div><div className="col-md-2"><label className="form-label">Cantidad</label><input required min="0.01" step="0.01" type="number" className="form-control" value={form.cantidad} onChange={update('cantidad')} /></div><div className="col-md-2"><label className="form-label">Total pagado</label><input required min="0.01" step="0.01" type="number" className="form-control" value={form.valor_pagado} onChange={update('valor_pagado')} /></div><div className="col-md-4"><label className="form-label">Fecha</label><input required type="date" className="form-control" value={form.fecha} onChange={update('fecha')} /></div><div className="col-md-4"><label className="form-label">Libro fiscal</label><select required className="form-select" value={form.libro} onChange={update('libro')}><option value="">Seleccione</option>{libros.map((row) => <option key={row.id} value={row.id}>{row.nombre} ({row.anio})</option>)}</select></div><div className="col-md-4 d-flex align-items-end"><button className="btn btn-primary w-100">Registrar compra</button></div></div></form></div>}
    <div className="data-table"><div className="table-header"><h5>Historial de egresos</h5></div><div className="table-responsive"><table><thead><tr><th>Fecha</th><th>Proveedor</th><th>NIT</th><th>Producto</th><th>Descripción</th><th className="text-end">Pagado</th><th>Libro</th></tr></thead><tbody>{expenses.map((row) => { const provider = providers.find((item) => item.id === row.provider); return <tr key={row.id}><td>{row.fecha}</td><td>{row.provider_nombre}</td><td>{provider?.nit || '-'}</td><td>{row.descripcion_producto}</td><td>{row.descripcion}</td><td className="text-end">{Number(row.valor_pagado).toFixed(2)}</td><td>{row.libro}</td></tr>; })}{!expenses.length && <tr><td colSpan="7" className="text-center text-muted py-3">Sin egresos registrados.</td></tr>}</tbody></table></div></div></div>;
}
