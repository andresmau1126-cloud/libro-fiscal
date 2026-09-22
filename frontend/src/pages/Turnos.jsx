import { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { abrirTurno, cerrarTurno, editarHorasTurno, fetchTurnos, fetchTurnosReporte, fetchTurnosVendedores } from '../services/api';

const money = (value) => '$ ' + Number(value || 0).toLocaleString('es-CO', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const localDate = () => {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
};

export default function Turnos() {
  const { user } = useAuth();
  const isSupervisor = ['admin', 'gerente'].includes(user?.rol);
  const today = localDate();

  const [turnos, setTurnos] = useState([]);
  const [ausentes, setAusentes] = useState([]);
  const [vendedores, setVendedores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  // Filtros solo para gerente/admin
  const [filtroVendedor, setFiltroVendedor] = useState('');
  const [filtroFecha, setFiltroFecha] = useState(today);
  const [filtroEstado, setFiltroEstado] = useState('');

  // Formularios del vendedor
  const [cajaInicial, setCajaInicial] = useState('');
  const [totalEntregado, setTotalEntregado] = useState('');
  const [forzarEntregado, setForzarEntregado] = useState({});
  const [saving, setSaving] = useState(false);

  // Edición independiente de hora entrada/salida (no requiere montos)
  const [editHoras, setEditHoras] = useState({});

  // Formulario de gerente/admin para abrir turno a nombre de un vendedor
  const [nuevoVendedorId, setNuevoVendedorId] = useState('');
  const [nuevaCajaInicial, setNuevaCajaInicial] = useState('');
  const [nuevaHoraEntrada, setNuevaHoraEntrada] = useState('');
  const [forzarHoraSalida, setForzarHoraSalida] = useState({});

  const misTurnos = useMemo(
    () => turnos.filter((t) => t.vendedor === user?.id),
    [turnos, user?.id],
  );
  const miTurnoHoy = useMemo(
    () => misTurnos.find((t) => t.fecha === today),
    [misTurnos, today],
  );

  const load = async () => {
    setLoading(true);
    try {
      if (isSupervisor) {
        const params = {};
        if (filtroFecha) params.fecha = filtroFecha;
        if (filtroVendedor) params.vendedor = filtroVendedor;
        if (filtroEstado) params.estado = filtroEstado;
        const [rows, reporte] = await Promise.all([
          fetchTurnos(params),
          fetchTurnosReporte(filtroFecha || today),
        ]);
        setTurnos(rows);
        setAusentes(reporte?.resumen?.ausentes || []);
      } else {
        const rows = await fetchTurnos();
        setTurnos(rows);
      }
    } catch (error) {
      setMessage({ ok: false, text: 'No se pudieron cargar los turnos.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [isSupervisor, filtroFecha, filtroVendedor, filtroEstado]);

  useEffect(() => {
    if (!isSupervisor) return;
    fetchTurnosVendedores()
      .then((rows) => setVendedores(rows))
      .catch(() => {});
  }, [isSupervisor]);

  const handleAbrir = async (event) => {
    event.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      await abrirTurno({ caja_inicial: Number(cajaInicial || 0) });
      setCajaInicial('');
      setMessage({ ok: true, text: 'Turno abierto correctamente.' });
      await load();
    } catch (error) {
      setMessage({ ok: false, text: error?.response?.data?.error || 'No se pudo abrir el turno.' });
    } finally {
      setSaving(false);
    }
  };

  const handleCerrar = async (event) => {
    event.preventDefault();
    if (!miTurnoHoy) return;
    setSaving(true);
    setMessage(null);
    try {
      await cerrarTurno({ turno_id: miTurnoHoy.id, total_entregado: Number(totalEntregado || 0) });
      setTotalEntregado('');
      setMessage({ ok: true, text: 'Turno cerrado correctamente.' });
      await load();
    } catch (error) {
      setMessage({ ok: false, text: error?.response?.data?.error || 'No se pudo cerrar el turno.' });
    } finally {
      setSaving(false);
    }
  };

  const handleForzarCierre = async (turno) => {
    const valor = Number(forzarEntregado[turno.id] || 0);
    const horaSalida = forzarHoraSalida[turno.id];
    setSaving(true);
    setMessage(null);
    try {
      const payload = { turno_id: turno.id, total_entregado: valor };
      if (horaSalida) payload.hora_salida = new Date(horaSalida).toISOString();
      await cerrarTurno(payload);
      setMessage({ ok: true, text: `Turno de ${turno.vendedor_nombre} cerrado.` });
      await load();
    } catch (error) {
      setMessage({ ok: false, text: error?.response?.data?.error || 'No se pudo forzar el cierre.' });
    } finally {
      setSaving(false);
    }
  };

  const handleAbrirParaVendedor = async (event) => {
    event.preventDefault();
    if (!nuevoVendedorId) return;
    setSaving(true);
    setMessage(null);
    try {
      const payload = { vendedor_id: Number(nuevoVendedorId), caja_inicial: Number(nuevaCajaInicial || 0) };
      if (nuevaHoraEntrada) payload.hora_entrada = new Date(nuevaHoraEntrada).toISOString();
      await abrirTurno(payload);
      setNuevoVendedorId('');
      setNuevaCajaInicial('');
      setNuevaHoraEntrada('');
      setMessage({ ok: true, text: 'Turno abierto correctamente.' });
      await load();
    } catch (error) {
      setMessage({ ok: false, text: error?.response?.data?.error || 'No se pudo abrir el turno.' });
    } finally {
      setSaving(false);
    }
  };

  const handleEditarHoras = async (turno) => {
    const valores = editHoras[turno.id] || {};
    const payload = {};
    if (valores.hora_entrada) payload.hora_entrada = new Date(valores.hora_entrada).toISOString();
    if (valores.hora_salida) payload.hora_salida = new Date(valores.hora_salida).toISOString();
    if (!payload.hora_entrada && !payload.hora_salida) return;
    setSaving(true);
    setMessage(null);
    try {
      await editarHorasTurno(turno.id, payload);
      setEditHoras({ ...editHoras, [turno.id]: {} });
      setMessage({ ok: true, text: `Horas de ${turno.vendedor_nombre} actualizadas.` });
      await load();
    } catch (error) {
      setMessage({ ok: false, text: error?.response?.data?.error || 'No se pudieron actualizar las horas.' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="d-flex justify-content-center p-5"><div className="spinner-border text-primary" /></div>;
  }

  return (
    <div>
      <h2><i className="bi bi-clock-history me-2" />Control de Turnos</h2>

      {message && (
        <div className={`alert ${message.ok ? 'alert-success' : 'alert-danger'}`}>{message.text}</div>
      )}

      {!isSupervisor && (
        <div className="card mb-4">
          <div className="card-body">
            <h5 className="card-title">Mi turno de hoy</h5>
            {miTurnoHoy ? (
              <div>
                <p>
                  Estado: <strong className={miTurnoHoy.estado === 'abierto' ? 'text-success' : 'text-secondary'}>
                    {miTurnoHoy.estado === 'abierto' ? 'Abierto' : 'Cerrado'}
                  </strong>
                </p>
                <p>Caja inicial: {money(miTurnoHoy.caja_inicial)}</p>
                {miTurnoHoy.estado === 'cerrado' && (
                  <>
                    <p>Ventas del día: {money(miTurnoHoy.ventas_dia)}</p>
                    <p>Total entregado: {money(miTurnoHoy.total_entregado)}</p>
                    <p>
                      Faltante:{' '}
                      <strong className={Number(miTurnoHoy.faltante) > 0 ? 'text-danger' : 'text-success'}>
                        {money(miTurnoHoy.faltante)}
                      </strong>
                    </p>
                  </>
                )}
                {miTurnoHoy.estado === 'abierto' && (
                  <form className="row g-2 align-items-end" onSubmit={handleCerrar}>
                    <div className="col-auto">
                      <label className="form-label">Total entregado</label>
                      <input
                        type="number" min="0" step="0.01" className="form-control"
                        value={totalEntregado} onChange={(e) => setTotalEntregado(e.target.value)} required
                      />
                    </div>
                    <div className="col-auto">
                      <button type="submit" className="btn btn-danger" disabled={saving}>Cerrar Turno</button>
                    </div>
                  </form>
                )}
              </div>
            ) : (
              <form className="row g-2 align-items-end" onSubmit={handleAbrir}>
                <div className="col-auto">
                  <label className="form-label">Caja inicial</label>
                  <input
                    type="number" min="0" step="0.01" className="form-control"
                    value={cajaInicial} onChange={(e) => setCajaInicial(e.target.value)} required
                  />
                </div>
                <div className="col-auto">
                  <button type="submit" className="btn btn-success" disabled={saving}>Abrir Turno</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {isSupervisor && (
        <>
          <div className="card mb-3">
            <div className="card-body">
              <h5 className="card-title">Abrir turno para un vendedor</h5>
              <form className="row g-2 align-items-end" onSubmit={handleAbrirParaVendedor}>
                <div className="col-auto">
                  <label className="form-label">Vendedor</label>
                  <select className="form-select" value={nuevoVendedorId} onChange={(e) => setNuevoVendedorId(e.target.value)} required>
                    <option value="">Seleccione un vendedor...</option>
                    {vendedores.map((v) => (
                      <option key={v.id} value={v.id}>{v.nombre}</option>
                    ))}
                  </select>
                </div>
                <div className="col-auto">
                  <label className="form-label">Caja inicial</label>
                  <input
                    type="number" min="0" step="0.01" className="form-control"
                    value={nuevaCajaInicial} onChange={(e) => setNuevaCajaInicial(e.target.value)} required
                  />
                </div>
                <div className="col-auto">
                  <label className="form-label">Hora de entrada (opcional)</label>
                  <input
                    type="datetime-local" className="form-control"
                    value={nuevaHoraEntrada} onChange={(e) => setNuevaHoraEntrada(e.target.value)}
                  />
                </div>
                <div className="col-auto">
                  <button type="submit" className="btn btn-success" disabled={saving}>Abrir Turno</button>
                </div>
              </form>
            </div>
          </div>

          <div className="card mb-3">
            <div className="card-body">
              <div className="row g-2">
                <div className="col-auto">
                  <label className="form-label">Fecha</label>
                  <input type="date" className="form-control" value={filtroFecha} onChange={(e) => setFiltroFecha(e.target.value)} />
                </div>
                <div className="col-auto">
                  <label className="form-label">Vendedor</label>
                  <input type="text" className="form-control" placeholder="Buscar vendedor..." value={filtroVendedor} onChange={(e) => setFiltroVendedor(e.target.value)} />
                </div>
                <div className="col-auto">
                  <label className="form-label">Estado</label>
                  <select className="form-select" value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}>
                    <option value="">Todos</option>
                    <option value="abierto">Abierto</option>
                    <option value="cerrado">Cerrado</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {ausentes.length > 0 && (
            <div className="alert alert-warning">
              <strong>Vendedores sin turno hoy:</strong> {ausentes.map((a) => a.nombre).join(', ')}
            </div>
          )}

          <div className="table-responsive">
            <table className="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Vendedor</th>
                  <th>Fecha</th>
                  <th>Entrada</th>
                  <th>Salida</th>
                  <th>Estado</th>
                  <th>Caja inicial</th>
                  <th>Ventas del día</th>
                  <th>Entregado</th>
                  <th>Faltante</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                {turnos.map((t) => (
                  <tr key={t.id}>
                    <td>{t.vendedor_nombre}</td>
                    <td>{t.fecha}</td>
                    <td>{t.hora_entrada ? new Date(t.hora_entrada).toLocaleTimeString('es-CO') : '-'}</td>
                    <td>{t.hora_salida ? new Date(t.hora_salida).toLocaleTimeString('es-CO') : '-'}</td>
                    <td>
                      <span className={`badge ${t.estado === 'abierto' ? 'bg-success' : 'bg-secondary'}`}>
                        {t.estado === 'abierto' ? 'Abierto' : 'Cerrado'}
                      </span>
                    </td>
                    <td>{money(t.caja_inicial)}</td>
                    <td>{money(t.ventas_dia)}</td>
                    <td>{t.total_entregado != null ? money(t.total_entregado) : '-'}</td>
                    <td>
                      {t.faltante != null ? (
                        <strong className={Number(t.faltante) > 0 ? 'text-danger' : 'text-success'}>
                          {money(t.faltante)}
                        </strong>
                      ) : '-'}
                    </td>
                    <td>
                      <div className="d-flex gap-2 align-items-end flex-wrap mb-2">
                        <div>
                          <label className="form-label small mb-0">Entrada</label>
                          <input
                            type="datetime-local" className="form-control form-control-sm" style={{ width: 180 }}
                            value={editHoras[t.id]?.hora_entrada || ''}
                            onChange={(e) => setEditHoras({ ...editHoras, [t.id]: { ...editHoras[t.id], hora_entrada: e.target.value } })}
                          />
                        </div>
                        <div>
                          <label className="form-label small mb-0">Salida</label>
                          <input
                            type="datetime-local" className="form-control form-control-sm" style={{ width: 180 }}
                            value={editHoras[t.id]?.hora_salida || ''}
                            onChange={(e) => setEditHoras({ ...editHoras, [t.id]: { ...editHoras[t.id], hora_salida: e.target.value } })}
                          />
                        </div>
                        <button
                          className="btn btn-sm btn-outline-primary"
                          disabled={saving}
                          onClick={() => handleEditarHoras(t)}
                        >
                          Guardar horas
                        </button>
                      </div>
                      {t.estado === 'abierto' && (
                        <div className="d-flex gap-2 align-items-end flex-wrap">
                          <div>
                            <label className="form-label small mb-0">Entregado (opcional)</label>
                            <input
                              type="number" min="0" step="0.01" className="form-control form-control-sm" style={{ width: 110 }}
                              placeholder="0.00"
                              value={forzarEntregado[t.id] || ''}
                              onChange={(e) => setForzarEntregado({ ...forzarEntregado, [t.id]: e.target.value })}
                            />
                          </div>
                          <div>
                            <label className="form-label small mb-0">Hora salida (opcional)</label>
                            <input
                              type="datetime-local" className="form-control form-control-sm" style={{ width: 180 }}
                              value={forzarHoraSalida[t.id] || ''}
                              onChange={(e) => setForzarHoraSalida({ ...forzarHoraSalida, [t.id]: e.target.value })}
                            />
                          </div>
                          <button
                            className="btn btn-sm btn-outline-danger"
                            disabled={saving}
                            onClick={() => handleForzarCierre(t)}
                          >
                            Forzar cierre
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
                {turnos.length === 0 && (
                  <tr><td colSpan={10} className="text-center text-muted">Sin turnos para los filtros seleccionados.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
