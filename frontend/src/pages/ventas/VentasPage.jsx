import { useEffect, useMemo, useState } from 'react';
import { createVenta, deleteVenta, fetchProductos, fetchVentas } from '../../services/api';

const money = (value) => '$ ' + Number(value || 0).toLocaleString('es-CO', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const localDate = () => {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
};

const STORAGE_KEY = 'libro-fiscal-tender-state-v1';

export default function VentasPage() {
  const today = localDate();
  const getInitialState = () => {
    if (typeof window === 'undefined') return null;
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return {
        fecha: parsed.fecha || today,
        cliente: parsed.cliente || '',
        medioPago: parsed.medioPago || 'efectivo',
        cart: Array.isArray(parsed.cart) ? parsed.cart : [],
      };
    } catch {
      return null;
    }
  };

  const initialState = getInitialState();

  const [productos, setProductos] = useState([]);
  const [ventas, setVentas] = useState([]);
  const [fecha, setFecha] = useState(initialState?.fecha || today);
  const [cliente, setCliente] = useState(initialState?.cliente || '');
  const [medioPago, setMedioPago] = useState(initialState?.medioPago || 'efectivo');
  const [cart, setCart] = useState(initialState?.cart || []);
  const [selectedId, setSelectedId] = useState('');
  const [cantidad, setCantidad] = useState('1');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const payload = JSON.stringify({ fecha, cliente, medioPago, cart });
      window.localStorage.setItem(STORAGE_KEY, payload);
    }
  }, [fecha, cliente, medioPago, cart]);

  const load = async () => {
    setLoading(true);
    try {
      const [productData, saleData] = await Promise.all([fetchProductos(), fetchVentas(fecha)]);
      setProductos(productData || []);
      setVentas(saleData?.ventas || []);
    } catch (error) {
      setMessage({ ok: false, text: error.response?.data?.error || 'No se pudo cargar la caja.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [fecha]);

  const total = useMemo(() => cart.reduce((sum, item) => sum + item.cantidad * item.precio_venta, 0), [cart]);

  const addProduct = () => {
    const product = productos.find((item) => String(item.id) === String(selectedId));
    const qty = Number(cantidad);
    if (!product || !qty || qty <= 0) return;
    setCart((current) => {
      const existing = current.find((item) => item.id === product.id);
      if (existing) return current.map((item) => item.id === product.id ? { ...item, cantidad: item.cantidad + qty } : item);
      return [...current, { ...product, cantidad: qty }];
    });
    setSelectedId('');
    setCantidad('1');
  };

  const checkout = async (event) => {
    event.preventDefault();
    if (!cart.length) return;
    setSaving(true);
    setMessage(null);
    try {
      await createVenta({
        cliente,
        medio_pago: medioPago,
        detalles: cart.map((item) => ({ producto_id: item.id, cantidad: item.cantidad })),
      });
      const soldIds = new Set(cart.map((item) => item.id));
      setCart([]);
      setCliente('');
      setMedioPago('efectivo');
      setSelectedId('');
      setCantidad('1');
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(STORAGE_KEY);
      }
      setMessage({ ok: true, text: 'Venta registrada y stock actualizado.' });
      await load();
      setProductos((current) => current.filter((product) => !soldIds.has(product.id) || Number(product.stock_actual) > 0));
    } catch (error) {
      setMessage({ ok: false, text: error.response?.data?.error || 'No se pudo registrar la venta.' });
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteVenta = async (ventaId, ventaTotal) => {
    if (!window.confirm(`¿Eliminar venta #${ventaId} (${money(ventaTotal)})? Se restaurará el stock.`)) return;
    setSaving(true);
    setMessage(null);
    try {
      await deleteVenta(ventaId);
      setMessage({ ok: true, text: 'Venta eliminada y stock restaurado.' });
      await load();
    } catch (error) {
      setMessage({ ok: false, text: error.response?.data?.error || 'No se pudo eliminar la venta.' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container-fluid py-3">
      <div className="page-header mb-3">
        <h2><i className="bi bi-cart3 me-2" />Punto de venta</h2>
        <p>Registra ventas de productos de refrigeración y descuenta existencias automáticamente.</p>
      </div>

      {message && <div className={`alert ${message.ok ? 'alert-success' : 'alert-danger'} py-2`}>{message.text}</div>}

      <div className="row g-3 align-items-start">
        <div className="col-lg-7">
          <div className="data-table p-3">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div><h5 className="mb-0">Nueva venta</h5><small className="text-muted">El stock se actualiza al confirmar el cobro.</small></div>
              <span className="badge text-bg-light">{cart.length} productos</span>
            </div>
            <form onSubmit={checkout}>
              <div className="row g-2 mb-3">
                <div className="col-md-7">
                  <label className="form-label small">Producto</label>
                  <select className="form-select" value={selectedId} onChange={(event) => setSelectedId(event.target.value)}>
                    <option value="">Seleccione un producto</option>
                    {productos.filter((item) => !item.vencido && Number(item.stock_actual) > 0).map((item) => (
                      <option key={item.id} value={item.id}>{item.nombre} | {money(item.precio_venta)} | stock {item.stock_actual}</option>
                    ))}
                  </select>
                </div>
                <div className="col-md-3">
                  <label className="form-label small">Cantidad</label>
                  <input className="form-control" type="number" min="0.01" step="0.01" value={cantidad} onChange={(event) => setCantidad(event.target.value)} />
                </div>
                <div className="col-md-2 d-flex align-items-end">
                  <button type="button" className="btn btn-outline-primary w-100" onClick={addProduct}>Agregar</button>
                </div>
              </div>

              <div className="table-responsive mb-3">
                <table className="table align-middle mb-0">
                  <thead><tr><th>Producto</th><th className="text-end">Cant.</th><th className="text-end">Subtotal</th><th /></tr></thead>
                  <tbody>
                    {!cart.length && <tr><td colSpan="4" className="text-center text-muted py-4">Agregue productos para iniciar la venta.</td></tr>}
                    {cart.map((item) => (
                      <tr key={item.id}>
                        <td>{item.nombre}<div className="small text-muted">{money(item.precio_venta)} c/u</div></td>
                        <td className="text-end">{item.cantidad}</td>
                        <td className="text-end fw-semibold">{money(item.cantidad * item.precio_venta)}</td>
                        <td className="text-end"><button type="button" className="btn btn-sm btn-outline-danger" aria-label={`Quitar ${item.nombre}`} onClick={() => setCart(cart.filter((line) => line.id !== item.id))}><i className="bi bi-trash" /></button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="row g-2">
                <div className="col-md-5"><label className="form-label small">Cliente (opcional)</label><input className="form-control" value={cliente} onChange={(event) => setCliente(event.target.value)} placeholder="Consumidor final" /></div>
                <div className="col-md-4"><label className="form-label small">Medio de pago</label><select className="form-select" value={medioPago} onChange={(event) => setMedioPago(event.target.value)}><option value="efectivo">Efectivo</option><option value="transferencia">Transferencia</option><option value="tarjeta">Tarjeta</option></select></div>
                <div className="col-md-3 d-flex align-items-end"><button className="btn btn-primary w-100" disabled={saving || !cart.length}>{saving ? 'Registrando...' : `Cobrar ${money(total)}`}</button></div>
              </div>
            </form>
          </div>
        </div>

        <div className="col-lg-5">
          <div className="data-table p-3">
            <div className="d-flex justify-content-between align-items-center mb-3"><h5 className="mb-0">Ventas del día</h5><div className="d-flex gap-2"><input type="date" className="form-control form-control-sm w-auto" value={fecha} onChange={(event) => setFecha(event.target.value)} /><button type="button" className="btn btn-sm btn-outline-secondary" onClick={load} disabled={loading} title="Actualizar ventas y stock" aria-label="Actualizar ventas y stock"><i className="bi bi-arrow-clockwise" /></button></div></div>
            <div className="display-6 fw-semibold text-success mb-3">{money(ventas.reduce((sum, sale) => sum + sale.total, 0))}</div>
            {loading ? <div className="text-muted">Cargando...</div> : !ventas.length ? <div className="text-muted">No hay ventas para esta fecha.</div> : ventas.map((sale) => <div className="border-top py-2" key={sale.id}><div className="d-flex justify-content-between align-items-start"><div><strong>Venta #{sale.id}</strong><div className="small text-muted">{new Date(sale.fecha).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })} · {sale.medio_pago} · {sale.cliente || 'Consumidor final'}</div>{sale.vendedor && <div className="small text-muted">Vendedor: {sale.vendedor} ({sale.vendedor_rol === 'vendedor_2' ? 'Vendedor 2' : 'Vendedor'})</div>}</div><div className="text-end"><div>{money(sale.total)}</div><button type="button" className="btn btn-sm btn-outline-danger mt-1" onClick={() => handleDeleteVenta(sale.id, sale.total)} disabled={saving} title="Eliminar venta"><i className="bi bi-trash" /></button></div></div></div>)}
          </div>
        </div>
      </div>
    </div>
  );
}