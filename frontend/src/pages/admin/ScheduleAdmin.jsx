import { useEffect, useState } from 'react';
import { fetchSchedules, updateSchedule } from '../../services/api';

export default function ScheduleAdmin() {
  const [schedules, setSchedules] = useState([]);
  const [message, setMessage] = useState(null);
  const [savingId, setSavingId] = useState(null);

  const load = async () => {
    try {
      setSchedules(await fetchSchedules());
    } catch (error) {
      setMessage({ ok: false, text: error.response?.data?.error || 'No se pudieron cargar los horarios.' });
    }
  };

  useEffect(() => { load(); }, []);

  const updateField = (id, field, value) => {
    setSchedules((current) => current.map((schedule) => (
      schedule.id === id ? { ...schedule, [field]: value } : schedule
    )));
  };

  const save = async (schedule) => {
    setSavingId(schedule.id);
    setMessage(null);
    try {
      const updated = await updateSchedule(schedule.id, {
        start_time: schedule.start_time,
        end_time: schedule.end_time,
      });
      setSchedules((current) => current.map((item) => item.id === schedule.id ? updated : item));
      setMessage({ ok: true, text: 'Horario actualizado.' });
    } catch (error) {
      setMessage({ ok: false, text: error.response?.data?.error || 'No se pudo actualizar el horario.' });
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="container-fluid py-3">
      <div className="page-header mb-3">
        <h2><i className="bi bi-clock me-2" />Horarios de vendedores</h2>
        <p>Configura los turnos asociados al email de cada vendedor.</p>
      </div>
      {message && <div className={`alert ${message.ok ? 'alert-success' : 'alert-danger'}`}>{message.text}</div>}
      <div className="data-table">
        <div className="table-header"><h5>Turnos ({schedules.length})</h5></div>
        <div className="table-responsive">
          <table>
            <thead>
              <tr><th>Email</th><th>Nombre</th><th>Inicio</th><th>Fin</th><th className="text-end">Acción</th></tr>
            </thead>
            <tbody>
              {schedules.map((schedule) => (
                <tr key={schedule.id}>
                  <td>{schedule.usuario_email}</td>
                  <td>{schedule.name}</td>
                  <td>
                    <input
                      type="time"
                      className="form-control"
                      value={schedule.start_time?.slice(0, 5) || ''}
                      onChange={(event) => updateField(schedule.id, 'start_time', event.target.value)}
                    />
                  </td>
                  <td>
                    <input
                      type="time"
                      className="form-control"
                      value={schedule.end_time?.slice(0, 5) || ''}
                      onChange={(event) => updateField(schedule.id, 'end_time', event.target.value)}
                    />
                  </td>
                  <td className="text-end">
                    <button
                      type="button"
                      className="btn btn-sm btn-primary"
                      onClick={() => save(schedule)}
                      disabled={savingId === schedule.id}
                    >
                      {savingId === schedule.id ? 'Guardando...' : 'Guardar'}
                    </button>
                  </td>
                </tr>
              ))}
              {!schedules.length && <tr><td colSpan="5" className="text-center text-muted py-3">Sin horarios configurados.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
