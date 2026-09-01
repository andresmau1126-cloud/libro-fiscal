import { useEffect, useMemo, useState } from 'react';
import { fetchVentas } from '../../services/api';

const money = (value) => '$ ' + Number(value || 0).toLocaleString('es-CO', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const formatDate = (value) => {
  if (!value) return '—';
  const dt = new Date(value);
  if (Number.isNaN(dt.getTime())) return value;
  return dt.toLocaleString('es-CO', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export default function VentasControlPage() {
  const [ventas, setVentas] = useState([]);
  const [fecha, setFecha] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async (selectedDate = '') => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchVentas(selectedDate);
      setVentas(data?.ventas || []);
    } catch (err) {
      setError(err.response?.data?.error || 'No se pudo cargar el control de ventas.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(fecha);
  }, [fecha]);

  const grouped = useMemo(() => {
    const map = new Map();
    ventas.forEach((sale) => {
      const key = sale.vendedor || 'Sin vendedor';
      const group = map.get(key) || {
        vendedor: sale.vendedor,
        rol: sale.vendedor_rol,
        ventas: [],
        total: 0,
      };
      group.ventas.push(sale);
      group.total += Number(sale.total || 0);
      map.set(key, group);
    });
    return [...map.values()].sort((a, b) => b.total - a.total);
  }, [ventas]);

  const totalGeneral = ventas.reduce((sum, sale) => sum + Number(sale.total || 0), 0);

  return (
    <div className="container-fluid py-3">
      <div className="page-header mb-3">
        <h2><i className="bi bi-clipboard-data me-2" />Control de ventas por vendedor</h2>
        <p>Supervisa las ventas de cada vendedor y compara el desempeño por día.</p>
      </div>

      {error && <div className="alert alert-danger py-2">{error}</div>}

      <div className="data-table p-3 mb-4">
        <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2">
          <div>
            <h5 className="mb-0">Resumen</h5>
          </div>
          <div className="d-flex align-items-center gap-2">
            <label className="small text-muted mb-0">Fecha</label>
            <input
              type="date"
              className="form-control form-control-sm"
              value={fecha}
              onChange={(event) => setFecha(event.target.value)}
            />
            <button className="btn btn-outline-secondary btn-sm" onClick={() => load(fecha)} disabled={loading}>
              <i className="bi bi-arrow-clockwise me-1" />Actualizar
            </button>
          </div>
        </div>

        <div className="row g-3 mt-1">
          <div className="col-md-4">
            <div className="stat-card compact">
              <div className="stat-icon" style={{ background: '#dbeafe', color: '#1d4ed8' }}>
                <i className="bi bi-cash-stack" />
              </div>
              <div>
                <div className="stat-label">Ventas</div>
                <div className="stat-value">{ventas.length}</div>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="stat-card compact">
              <div className="stat-icon" style={{ background: '#dcfce7', color: '#15803d' }}>
                <i className="bi bi-wallet2" />
              </div>
              <div>
                <div className="stat-label">Total</div>
                <div className="stat-value">{money(totalGeneral)}</div>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="stat-card compact">
              <div className="stat-icon" style={{ background: '#f3e8ff', color: '#7c3aed' }}>
                <i className="bi bi-people-fill" />
              </div>
              <div>
                <div className="stat-label">Vendedores</div>
                <div className="stat-value">{grouped.length}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-5 text-muted">Cargando ventas...</div>
      ) : grouped.length === 0 ? (
        <div className="alert alert-light border text-center py-4">No hay ventas registradas para este filtro.</div>
      ) : (
        grouped.map((group) => (
          <div className="data-table p-3 mb-4" key={group.vendedor || 'sin-vendedor'}>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 className="mb-0">{group.vendedor || 'Sin vendedor'}</h5>
                <small className="text-muted">{group.rol === 'vendedor_2' ? 'Vendedor 2' : 'Vendedor'}</small>
              </div>
              <span className="badge text-bg-success rounded-pill px-3 py-2">{money(group.total)}</span>
            </div>

            <div className="table-responsive">
              <table className="table align-middle mb-0">
                <thead>
                  <tr>
                    <th>Venta</th>
                    <th>Productos</th>
                    <th>Cliente</th>
                    <th>Medio</th>
                    <th>Fecha</th>
                    <th className="text-end">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {group.ventas.map((sale) => (
                    <tr key={sale.id}>
                      <td>#{sale.id}</td>
                      <td>
                        {sale.detalles?.length ? sale.detalles.map((detalle) => (
                          <div key={detalle.producto_id}>
                            {detalle.producto} <span className="text-muted">x {detalle.cantidad}</span>
                            <div className="small text-muted">{money(detalle.subtotal)}</div>
                          </div>
                        )) : <span className="text-muted">Sin detalle</span>}
                      </td>
                      <td>{sale.cliente || 'Consumidor final'}</td>
                      <td>{sale.medio_pago}</td>
                      <td>{formatDate(sale.fecha)}</td>
                      <td className="text-end fw-semibold">{money(sale.total)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
