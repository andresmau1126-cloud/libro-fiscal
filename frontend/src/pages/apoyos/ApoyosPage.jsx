import { useState } from 'react';

const initialForm = {
  fecha: new Date().toISOString().slice(0, 10),
  hora: '09:00',
  observacion: '',
  confidencialidad: 'NO CONFIDENCIAL',
  proximoContacto: '',
  proximaHora: '09:00',
};

export default function ApoyosPage() {
  const [form, setForm] = useState(initialForm);
  const [apoyos, setApoyos] = useState([]);

  const updateField = event => {
    const { name, value } = event.target;
    setForm(current => ({ ...current, [name]: value }));
  };

  const handleSubmit = event => {
    event.preventDefault();
    if (!form.observacion.trim()) return;

    setApoyos(current => [{ ...form, id: Date.now() }, ...current]);
    setForm(current => ({ ...initialForm, fecha: current.fecha }));
  };

  return (
    <>
      <div className="page-header">
        <h2>Apoyos</h2>
        <p>Registra el seguimiento y los compromisos de cada encuentro.</p>
      </div>

      <div className="support-layout">
        <section className="form-card support-form-card">
          <div className="support-card-heading">
            <div className="support-icon"><i className="bi bi-person-hearts" /></div>
            <div>
              <h5>Nuevo apoyo</h5>
              <p>Completa la información del encuentro.</p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="support-fields-grid">
              <div className="form-group">
                <label htmlFor="fecha">Fecha de apoyo</label>
                <input id="fecha" name="fecha" type="date" value={form.fecha} onChange={updateField} required />
              </div>
              <div className="form-group">
                <label htmlFor="hora">Hora</label>
                <input id="hora" name="hora" type="time" value={form.hora} onChange={updateField} required />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="observacion">Observación</label>
              <textarea
                id="observacion"
                name="observacion"
                rows="7"
                value={form.observacion}
                onChange={updateField}
                placeholder="Describe el encuentro, los compromisos y el seguimiento acordado..."
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="confidencialidad">Confidencialidad</label>
              <select id="confidencialidad" name="confidencialidad" value={form.confidencialidad} onChange={updateField}>
                <option>NO CONFIDENCIAL</option>
                <option>CONFIDENCIAL</option>
              </select>
            </div>

            <div className="support-section-label">Próximo contacto <span>(opcional)</span></div>
            <div className="support-fields-grid">
              <div className="form-group">
                <label htmlFor="proximoContacto">Fecha</label>
                <input id="proximoContacto" name="proximoContacto" type="date" value={form.proximoContacto} onChange={updateField} />
              </div>
              <div className="form-group">
                <label htmlFor="proximaHora">Hora</label>
                <input id="proximaHora" name="proximaHora" type="time" value={form.proximaHora} onChange={updateField} />
              </div>
            </div>

            <button className="btn btn-primary support-submit" type="submit">
              <i className="bi bi-plus-circle me-2" />Insertar apoyo
            </button>
          </form>
        </section>

        <section className="support-history">
          <div className="support-history-heading">
            <div>
              <h5>Historial de apoyos</h5>
              <p>{apoyos.length} {apoyos.length === 1 ? 'registro' : 'registros'}</p>
            </div>
            <i className="bi bi-clock-history" />
          </div>
          {apoyos.length === 0 ? (
            <div className="support-empty">
              <i className="bi bi-journal-text" />
              <strong>Aún no hay apoyos registrados</strong>
              <span>El primer registro aparecerá aquí.</span>
            </div>
          ) : (
            <div className="support-records">
              {apoyos.map(apoyo => (
                <article className="support-record" key={apoyo.id}>
                  <div className="support-record-meta">
                    <span>{apoyo.fecha}</span><span>{apoyo.hora}</span>
                  </div>
                  <p>{apoyo.observacion}</p>
                  <small>{apoyo.confidencialidad}</small>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </>
  );
}