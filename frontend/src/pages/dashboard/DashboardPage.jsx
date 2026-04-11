import { useState, useEffect } from 'react';
import { fetchDashboard } from '../../services/api';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement,
  Title, Tooltip, Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const MES_ES = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

const fmt = (n) => Number(n || 0).toLocaleString('es-GT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="d-flex justify-content-center p-5"><div className="spinner-border text-primary" /></div>;
  if (!data) return <div className="alert alert-danger">Error al cargar dashboard</div>;

  const chartData = {
    labels: data.meses_chart?.map(m => MES_ES[m.mes]) || [],
    datasets: [
      {
        label: 'Ingresos',
        data: data.meses_chart?.map(m => m.ingresos) || [],
        backgroundColor: 'rgba(5, 150, 105, 0.7)',
        borderRadius: 6,
      },
      {
        label: 'Egresos',
        data: data.meses_chart?.map(m => m.egresos) || [],
        backgroundColor: 'rgba(220, 38, 38, 0.7)',
        borderRadius: 6,
      },
    ],
  };

  return (
    <>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Resumen general del sistema</p>
      </div>

      {/* KPI Cards */}
      <div className="row g-3 mb-4">
        <div className="col-sm-6 col-xl-3">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: '#dbeafe', color: '#1e40af' }}>
              <i className="bi bi-book-fill" />
            </div>
            <div className="stat-value">{data.total_libros}</div>
            <div className="stat-label">Libros</div>
          </div>
        </div>
        <div className="col-sm-6 col-xl-3">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: '#dcfce7', color: '#166534' }}>
              <i className="bi bi-arrow-down-circle-fill" />
            </div>
            <div className="stat-value text-success">Q{fmt(data.total_ingresos)}</div>
            <div className="stat-label">Ingresos</div>
          </div>
        </div>
        <div className="col-sm-6 col-xl-3">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: '#fee2e2', color: '#991b1b' }}>
              <i className="bi bi-arrow-up-circle-fill" />
            </div>
            <div className="stat-value text-danger">Q{fmt(data.total_egresos)}</div>
            <div className="stat-label">Egresos</div>
          </div>
        </div>
        <div className="col-sm-6 col-xl-3">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: '#e0e7ff', color: '#3730a3' }}>
              <i className="bi bi-wallet2" />
            </div>
            <div className="stat-value" style={{ color: data.saldo_global >= 0 ? '#059669' : '#dc2626' }}>
              Q{fmt(data.saldo_global)}
            </div>
            <div className="stat-label">Saldo</div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="row g-3 mb-4">
        <div className="col-lg-8">
          <div className="data-table">
            <div className="table-header">
              <h5>Ingresos vs Egresos (Año Actual)</h5>
            </div>
            <div style={{ padding: '1rem' }}>
              {data.meses_chart?.length > 0 ? (
                <Bar data={chartData} options={{ responsive: true, plugins: { legend: { position: 'top' } } }} />
              ) : (
                <p className="text-center text-muted py-4">Sin datos para graficar</p>
              )}
            </div>
          </div>
        </div>

        <div className="col-lg-4">
          <div className="data-table">
            <div className="table-header">
              <h5>Libros por Año</h5>
            </div>
            <div style={{ padding: '1rem' }}>
              {data.libros_por_anio?.map(l => (
                <div key={l.anio} className="d-flex justify-content-between py-2" style={{ borderBottom: '1px solid var(--gray-100)' }}>
                  <span className="fw-semibold">{l.anio}</span>
                  <span className="badge bg-primary rounded-pill">{l.cantidad}</span>
                </div>
              ))}
              {(!data.libros_por_anio || data.libros_por_anio.length === 0) && (
                <p className="text-muted text-center">Sin libros</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Recent transactions */}
      <div className="data-table">
        <div className="table-header">
          <h5>Últimos Movimientos</h5>
        </div>
        <table>
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Descripción</th>
              <th>Libro</th>
              <th className="text-end">Ingresos</th>
              <th className="text-end">Egresos</th>
              <th className="text-end">Saldo</th>
            </tr>
          </thead>
          <tbody>
            {data.movimientos_recientes?.map(m => (
              <tr key={m.id}>
                <td>{m.fecha}</td>
                <td>{m.descripcion}</td>
                <td>{m.libro_nombre || '—'}</td>
                <td className="text-end text-success">{fmt(m.ingresos)}</td>
                <td className="text-end text-danger">{fmt(m.egresos)}</td>
                <td className="text-end fw-semibold">{fmt(m.saldo)}</td>
              </tr>
            ))}
            {(!data.movimientos_recientes || data.movimientos_recientes.length === 0) && (
              <tr><td colSpan={6} className="text-center text-muted py-4">Sin movimientos</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
