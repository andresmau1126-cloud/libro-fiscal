import { useEffect, useState } from 'react';
import { createExpense, createProvider, fetchExpenses, fetchLibros, fetchProviders } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const initial = { provider: '', descripcion: '', fecha: new Date().toISOString().slice(0, 10), descripcion_producto: '', valor_unitario: '', valor_pagado: '', cantidad: '', libro: '' };

export default function ExpensesPage() {
  const { user } = useAuth();
  const readOnly = user?.rol === 'auditor';
  const [form, setForm] = useState(initial);
  const [providers, setProviders] = useState([]);
  const [libros, setLibros] = useState([]);
  const [expenses, setExpenses] = useState([]);
  const [message, setMessage] = useState(null);

  const load = async () => {
    const [providerRows, libroRows, expenseRows] = await Promise.all([fetchProviders(), fetchLibros(), fetchExpenses()]);
    setProviders(providerRows); setLibros(libroRows); setExpenses(expenseRows);
    setForm((current) => ({ ...current, provider: current.provider || providerRows[0]?.id || '', libro: current.libro || libroRows[0]?.id || '' }));
  };
  useEffect(() => { load().catch(() => setMessage({ ok: false, text: 'No se pudieron cargar los egresos.' })); }, []);
  const update = (field) => (event) => setForm({ ...form, [field]: event.target.value });
  const submit = async (event) => {
    event.preventDefault(); setMessage(null);
    try { await createExpense({ ...form, provider: Number(form.provider), libro: Number(form.libro) }); setForm({ ...initial, fecha: form.fecha, provider: form.provider, libro: form.libro }); setMessage({ ok: true, text: 'Egreso registrado en el libro fiscal.' }); await load(); }
    catch (error) { setMessage({ ok: false, text: error.response?.data?.error || 'No se pudo registrar el egreso.' }); }
  };
  const addProvider = async () => { const nombre = window.prompt('Nombre del proveedor'); if (!nombre) return; const provider = await createProvider({ nombre }); setProviders([...providers, provider]); setForm({ ...form, provider: provider.id }); };

  return <div className="container-fluid py-3"><div className="page-header mb-3"><h2><i className="bi bi-receipt me-2" />Egresos por proveedor</h2><p>Registra el detalle del pago y lo refleja automáticamente en el libro fiscal.</p></div>{message && <div className={`alert ${message.ok ? 'alert-success' : 'alert-danger'}`}>{message.text}</div>}
    {!readOnly && <div className="data-table p-3 mb-3"><form onSubmit={submit}><div className="row g-2"><div className="col-md-4"><label className="form-label">Proveedor</label><div className="input-group"><select required className="form-select" value={form.provider} onChange={update('provider')}><option value="">Seleccione</option>{providers.map((row) => <option key={row.id} value={row.id}>{row.nombre}</option>)}</select><button type="button" className="btn btn-outline-secondary" onClick={addProvider} title="Nuevo proveedor">+</button></div></div><div className="col-md-4"><label className="form-label">Descripción</label><input required className="form-control" value={form.descripcion} onChange={update('descripcion')} /></div><div className="col-md-4"><label className="form-label">Fecha</label><input required type="date" className="form-control" value={form.fecha} onChange={update('fecha')} /></div><div className="col-md-4"><label className="form-label">Descripción producto</label><input required className="form-control" value={form.descripcion_producto} onChange={update('descripcion_producto')} /></div><div className="col-md-2"><label className="form-label">Valor unitario</label><input required min="0.01" step="0.01" type="number" className="form-control" value={form.valor_unitario} onChange={update('valor_unitario')} /></div><div className="col-md-2"><label className="form-label">Valor pagado</label><input required min="0.01" step="0.01" type="number" className="form-control" value={form.valor_pagado} onChange={update('valor_pagado')} /></div><div className="col-md-2"><label className="form-label">Cantidad</label><input required min="0.01" step="0.01" type="number" className="form-control" value={form.cantidad} onChange={update('cantidad')} /></div><div className="col-md-2"><label className="form-label">Libro fiscal</label><select required className="form-select" value={form.libro} onChange={update('libro')}><option value="">Seleccione</option>{libros.map((row) => <option key={row.id} value={row.id}>{row.nombre} ({row.anio})</option>)}</select></div><div className="col-12 text-end"><button className="btn btn-primary">Registrar egreso</button></div></div></form></div>}
    <div className="data-table"><div className="table-header"><h5>Historial de egresos</h5></div><div className="table-responsive"><table><thead><tr><th>Fecha</th><th>Proveedor</th><th>Producto</th><th>Descripción</th><th className="text-end">Pagado</th><th>Libro</th></tr></thead><tbody>{expenses.map((row) => <tr key={row.id}><td>{row.fecha}</td><td>{row.provider_nombre}</td><td>{row.descripcion_producto}</td><td>{row.descripcion}</td><td className="text-end">{Number(row.valor_pagado).toFixed(2)}</td><td>{row.libro}</td></tr>)}{!expenses.length && <tr><td colSpan="6" className="text-center text-muted py-3">Sin egresos registrados.</td></tr>}</tbody></table></div></div></div>;
}
