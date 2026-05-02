import { useEffect, useMemo, useState } from 'react';
import {
  fetchProductos,
  createProducto,
  updateProducto,
  deleteProducto,
} from '../../services/api';

const fmtMoney = (n) => '$ ' + Number(n || 0).toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const EMPTY_FORM = {
  nombre: '',
  categoria: '',
  descripcion: '',
  stock_actual: '0',
  stock_minimo: '0',
  costo_unitario: '0',
  precio_venta: '0',
  fecha_vencimiento: '',
  dias_alerta: '30',
};

function EstadoBadge({ p }) {
  if (p.vencido)
    return <span className="badge bg-danger">Vencido</span>;
  if (p.por_vencer)
    return <span className="badge bg-warning text-dark">Vence en {p.dias_para_vencer}d</span>;
  if (p.stock_bajo)
    return <span className="badge bg-orange text-white" style={{ background: '#fd7e14' }}>Bajo stock</span>;
  return <span className="badge bg-success">OK</span>;
}

export default function InventarioPage() {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [soloBajoStock, setSoloBajoStock] = useState(false);
  const [error, setError] = useState('');
  const [flash, setFlash] = useState(null);

  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const showFlash = (msg, ok = true) => {
    setFlash({ msg, ok });
    setTimeout(() => setFlash(null), 2200);
  };

  const loadProductos = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchProductos(search, soloBajoStock);
      setProductos(data || []);
    } catch (err) {
      setError(err.response?.data?.error || 'No se pudo cargar el inventario.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadProductos(); }, [soloBajoStock]);

  /* ── Alertas de vencimiento ── */
  const alertas = useMemo(() =>
    productos.filter((p) => p.vencido || p.por_vencer),
    [productos]
  );

  const resumen = useMemo(() => {
    const total = productos.length;
    const bajoStock = productos.filter((p) => p.stock_bajo).length;
    const vencidos = productos.filter((p) => p.vencido).length;
    const porVencer = productos.filter((p) => p.por_vencer).length;
    return { total, bajoStock, vencidos, porVencer };
  }, [productos]);

  const resetForm = () => { setEditingId(null); setForm(EMPTY_FORM); };

  const openEdit = (p) => {
    setEditingId(p.id);
    setForm({
      nombre: p.nombre || '',
      categoria: p.categoria || '',
      descripcion: p.descripcion || '',
      stock_actual: String(p.stock_actual ?? 0),
      stock_minimo: String(p.stock_minimo ?? 0),
      costo_unitario: String(p.costo_unitario ?? 0),
      precio_venta: String(p.precio_venta ?? 0),
      fecha_vencimiento: p.fecha_vencimiento || '',
      dias_alerta: String(p.dias_alerta ?? 30),
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    const payload = {
      nombre: form.nombre.trim(),
      categoria: form.categoria.trim(),
      descripcion: form.descripcion.trim(),
      stock_actual: Number(form.stock_actual) || 0,
      stock_minimo: Number(form.stock_minimo) || 0,
      costo_unitario: Number(form.costo_unitario) || 0,
      precio_venta: Number(form.precio_venta) || 0,
      fecha_vencimiento: form.fecha_vencimiento || null,
      dias_alerta: Number(form.dias_alerta) || 30,
    };
    try {
      if (editingId) {
        await updateProducto(editingId, payload);
        showFlash('Producto actualizado');
      } else {
        await createProducto(payload);
        showFlash('Producto creado');
      }
      resetForm();
      await loadProductos();
    } catch (err) {
      setError(err.response?.data?.error || 'Error al guardar el producto.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id, nombre) => {
    if (!window.confirm(`¿Eliminar "${nombre}" del inventario?`)) return;
    try {
      await deleteProducto(id);
      showFlash('Producto eliminado');
      await loadProductos();
    } catch (err) {
      setError(err.response?.data?.error || 'Error al eliminar.');
    }
  };

  const handleSearch = async (e) => { e.preventDefault(); await loadProductos(); };

  return (
    <div className="container-fluid py-3">
      <div className="mb-3">
        <h3 className="mb-1">Inventario de Productos de Refrigeracion</h3>
        <p className="text-muted mb-0">Control de existencias y fechas de vencimiento.</p>
      </div>

      {/* ── Alertas de vencimiento ── */}
      {alertas.length > 0 && (
        <div className="alert alert-warning border-warning mb-3 p-2">
          <div className="fw-semibold mb-1">
            <i className="bi bi-exclamation-triangle-fill me-1" />
            Productos que requieren atención ({alertas.length})
          </div>
          <ul className="mb-0 ps-3">
            {alertas.map((p) => (
              <li key={p.id}>
                <strong>{p.nombre}</strong>
                {p.vencido
                  ? <span className="text-danger ms-1">— VENCIDO el {p.fecha_vencimiento}</span>
                  : <span className="text-warning ms-1">— vence en <strong>{p.dias_para_vencer} días</strong> ({p.fecha_vencimiento})</span>
                }
              </li>
            ))}
          </ul>
        </div>
      )}

      {flash && <div className={`alert ${flash.ok ? 'alert-success' : 'alert-danger'} py-2`}>{flash.msg}</div>}
      {error && <div className="alert alert-danger py-2">{error}</div>}

      {/* ── KPIs ── */}
      <div className="row g-3 mb-3">
        <div className="col-6 col-md-3">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-body">
              <small className="text-muted">Productos</small>
              <div className="fs-4 fw-bold">{resumen.total}</div>
            </div>
          </div>
        </div>
        <div className="col-6 col-md-3">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-body">
              <small className="text-muted">Bajo stock</small>
              <div className="fs-4 fw-bold text-danger">{resumen.bajoStock}</div>
            </div>
          </div>
        </div>
        <div className="col-6 col-md-3">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-body">
              <small className="text-muted">Por vencer</small>
              <div className="fs-4 fw-bold text-warning">{resumen.porVencer}</div>
            </div>
          </div>
        </div>
        <div className="col-6 col-md-3">
          <div className="card shadow-sm border-0 h-100">
            <div className="card-body">
              <small className="text-muted">Vencidos</small>
              <div className="fs-4 fw-bold text-danger">{resumen.vencidos}</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Formulario ── */}
      <div className="card shadow-sm border-0 mb-3">
        <div className="card-body">
          <h5 className="mb-3">{editingId ? 'Editar Producto' : 'Nuevo Producto'}</h5>
          <form className="row g-2" onSubmit={handleSubmit}>

            {/* Fila 1: datos básicos */}
            <div className="col-12 col-md-5">
              <label className="form-label mb-1 small">Nombre *</label>
              <input className="form-control" placeholder="Ej. Gas refrigerante R-22" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} required />
            </div>
            <div className="col-12 col-md-3">
              <label className="form-label mb-1 small">Categoría</label>
              <input className="form-control" placeholder="Ej. Refrigerantes" value={form.categoria} onChange={(e) => setForm({ ...form, categoria: e.target.value })} />
            </div>
            <div className="col-12 col-md-4">
              <label className="form-label mb-1 small">Descripción</label>
              <input className="form-control" placeholder="Descripción opcional" value={form.descripcion} onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
            </div>

            {/* Fila 2: vencimiento */}
            <div className="col-6 col-md-3">
              <label className="form-label mb-1 small">Fecha de vencimiento</label>
              <input type="date" className="form-control" value={form.fecha_vencimiento} onChange={(e) => setForm({ ...form, fecha_vencimiento: e.target.value })} />
            </div>
            <div className="col-6 col-md-2">
              <label className="form-label mb-1 small">Alertar (días antes)</label>
              <input type="number" min="1" className="form-control" placeholder="30" value={form.dias_alerta} onChange={(e) => setForm({ ...form, dias_alerta: e.target.value })} />
            </div>

            {/* Fila 3: stock y precios */}
            <div className="col-6 col-md-2">
              <label className="form-label mb-1 small">Stock actual</label>
              <input type="number" step="0.01" min="0" className="form-control" value={form.stock_actual} onChange={(e) => setForm({ ...form, stock_actual: e.target.value })} />
            </div>
            <div className="col-6 col-md-2">
              <label className="form-label mb-1 small">Stock mínimo</label>
              <input type="number" step="0.01" min="0" className="form-control" value={form.stock_minimo} onChange={(e) => setForm({ ...form, stock_minimo: e.target.value })} />
            </div>
            <div className="col-6 col-md-2">
              <label className="form-label mb-1 small">Costo unitario</label>
              <input type="number" step="0.01" min="0" className="form-control" value={form.costo_unitario} onChange={(e) => setForm({ ...form, costo_unitario: e.target.value })} />
            </div>
            <div className="col-6 col-md-2">
              <label className="form-label mb-1 small">Precio venta</label>
              <input type="number" step="0.01" min="0" className="form-control" value={form.precio_venta} onChange={(e) => setForm({ ...form, precio_venta: e.target.value })} />
            </div>

            <div className="col-12 d-flex gap-2 pt-1">
              <button className="btn btn-primary" disabled={saving}>{saving ? 'Guardando...' : editingId ? 'Actualizar' : 'Agregar'}</button>
              {editingId && <button type="button" className="btn btn-outline-secondary" onClick={resetForm}>Cancelar</button>}
            </div>
          </form>
        </div>
      </div>

      {/* ── Tabla ── */}
      <div className="card shadow-sm border-0">
        <div className="card-body">
          <div className="d-flex flex-wrap gap-2 justify-content-between align-items-center mb-3">
            <form className="d-flex gap-2" onSubmit={handleSearch}>
              <input className="form-control" placeholder="Buscar por nombre" value={search} onChange={(e) => setSearch(e.target.value)} />
              <button className="btn btn-outline-primary" type="submit">Buscar</button>
            </form>
            <div className="form-check form-switch mb-0">
              <input className="form-check-input" type="checkbox" checked={soloBajoStock} onChange={(e) => setSoloBajoStock(e.target.checked)} id="switchStock" />
              <label className="form-check-label" htmlFor="switchStock">Solo bajo stock</label>
            </div>
          </div>

          <div className="table-responsive">
            <table className="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Categoría</th>
                  <th className="text-end">Stock</th>
                  <th className="text-end">Costo</th>
                  <th className="text-end">Precio</th>
                  <th>Vencimiento</th>
                  <th className="text-center">Estado</th>
                  <th className="text-end">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {!loading && productos.length === 0 && (
                  <tr><td colSpan="8" className="text-center text-muted py-4">No hay productos registrados.</td></tr>
                )}
                {productos.map((p) => (
                  <tr key={p.id} className={p.vencido ? 'table-danger' : p.por_vencer ? 'table-warning' : ''}>
                    <td className="fw-semibold">{p.nombre}</td>
                    <td>{p.categoria || '-'}</td>
                    <td className="text-end">{Number(p.stock_actual).toLocaleString('es-CO')}</td>
                    <td className="text-end">{fmtMoney(p.costo_unitario)}</td>
                    <td className="text-end">{fmtMoney(p.precio_venta)}</td>
                    <td>{p.fecha_vencimiento || <span className="text-muted">—</span>}</td>
                    <td className="text-center"><EstadoBadge p={p} /></td>
                    <td className="text-end">
                      <div className="btn-group btn-group-sm">
                        <button className="btn btn-outline-primary" onClick={() => openEdit(p)}>Editar</button>
                        <button className="btn btn-outline-danger" onClick={() => handleDelete(p.id, p.nombre)}>Eliminar</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
