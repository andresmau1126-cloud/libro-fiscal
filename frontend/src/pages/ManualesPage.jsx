export default function ManualesPage() {
  return (
    <div className="container-fluid py-4">
      <div className="page-header mb-4">
        <h2><i className="bi bi-book me-2" />Manuales de Libro Fiscal</h2>
        <p>Guia tecnica y orden de procedimientos para la sustentacion.</p>
      </div>
      <div className="row g-3">
        <div className="col-lg-6">
          <div className="data-table p-4 h-100">
            <h5>Manual de usuario</h5>
            <ol>
              <li>Login con el perfil asignado.</li>
              <li>Registrar una venta y confirmar el stock.</li>
              <li>Registrar el egreso por proveedor.</li>
              <li>Consultar el libro fiscal del NIT 1010085627.</li>
              <li>Revisar estadisticas diarias y mensuales por vendedor.</li>
            </ol>
            <a className="btn btn-outline-primary" href="/docs/manual_usuario.md" target="_blank" rel="noreferrer">Abrir archivo del manual</a>
          </div>
        </div>
        <div className="col-lg-6">
          <div className="data-table p-4 h-100">
            <h5>Manual tecnico</h5>
            <p>Arquitectura Django + React, tablas, API REST, respaldo cada 24 horas y flujo venta a libro fiscal.</p>
            <a className="btn btn-outline-primary" href="/docs/manual_tecnico.md" target="_blank" rel="noreferrer">Abrir archivo tecnico</a>
          </div>
        </div>
      </div>
    </div>
  );
}
