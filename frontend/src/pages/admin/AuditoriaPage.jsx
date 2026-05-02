import { useState, useEffect } from 'react';
import { fetchAuditoria, clearAuditoria } from '../../services/api';

export default function AuditoriaPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAuditoria(200)
      .then(setLogs)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleClear = async () => {
    if (!window.confirm('¿Eliminar TODOS los registros de auditoría? Esta acción no se puede deshacer.')) return;
    try {
      await clearAuditoria();
      setLogs([]);
    } catch {
      alert('Error al limpiar la auditoría');
    }
  };

  return (
    <>
      <div className="page-header d-flex justify-content-between align-items-start">
        <div>
          <h2>Auditoría</h2>
          <p>Registro de acciones del sistema</p>
        </div>
        <button className="btn btn-outline-danger" onClick={handleClear}>
          <i className="bi bi-trash3 me-1" /> Limpiar todo
        </button>
      </div>

      <div className="data-table">
        <div className="table-header">
          <h5>Registros de Auditoría ({logs.length})</h5>
        </div>
        {loading ? (
          <div className="d-flex justify-content-center p-4"><div className="spinner-border text-primary" /></div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Usuario</th>
                <th>Acción</th>
                <th>Entidad</th>
                <th>ID</th>
                <th>IP</th>
                <th>Detalle</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(l => (
                <tr key={l.id}>
                  <td style={{ fontSize: '0.85rem', whiteSpace: 'nowrap' }}>{l.created_at?.slice(0, 19)}</td>
                  <td>{l.usuario_nombre || '—'}</td>
                  <td>
                    <span className="badge bg-info bg-opacity-10 text-dark" style={{ borderRadius: 8 }}>
                      {l.accion}
                    </span>
                  </td>
                  <td>{l.entidad}</td>
                  <td>{l.entidad_id || '—'}</td>
                  <td style={{ fontSize: '0.8rem' }}>{l.ip || '—'}</td>
                  <td style={{ fontSize: '0.8rem', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {l.detalle ? JSON.stringify(l.detalle) : '—'}
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr><td colSpan={7} className="text-center text-muted py-4">Sin registros</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
