import { useState, useEffect } from 'react';
import { fetchAuditoria, deleteAuditoria } from '../../services/api';

export default function AuditoriaPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    fetchAuditoria(200)
      .then(setLogs)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar este registro de auditoría?')) return;
    try {
      await deleteAuditoria(id);
      setLogs(prev => prev.filter(l => l.id !== id));
    } catch {
      alert('Error al eliminar el registro');
    }
  };

  return (
    <>
      <div className="page-header">
        <h2>Auditoría</h2>
        <p>Registro de acciones del sistema</p>
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
                <th></th>
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
                  <td>
                    <button
                      className="btn btn-sm btn-outline-danger"
                      title="Eliminar registro"
                      onClick={() => handleDelete(l.id)}
                    >
                      <i className="bi bi-trash" />
                    </button>
                  </td>
                </tr>
              ))}
              {logs.length === 0 && (
                <tr><td colSpan={8} className="text-center text-muted py-4">Sin registros</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
