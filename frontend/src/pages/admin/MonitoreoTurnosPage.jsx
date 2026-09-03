import React, { useState, useEffect } from "react";
import { Container, Row, Col, Card, Table, Button, Tabs, Tab, Alert } from "react-bootstrap";
import { api } from "../../services/api";
import "./MonitoreoTurnosPage.css";

const TURNO_LABELS = {
  mañana: "Mañana (06:00 - 14:00)",
  tarde: "Tarde (14:00 - 22:00)",
  noche: "Noche (22:00 - 06:00)",
};

const TURNO_COLORS = {
  mañana: "#4CAF50",  // Verde
  tarde: "#FF9800",   // Naranja
  noche: "#2196F3",   // Azul
};

function money(value) {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    minimumFractionDigits: 0,
  }).format(value);
}

export default function MonitoreoTurnosPage() {
  const [monitoreo, setMonitoreo] = useState(null);
  const [reportes, setReportes] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fechaInicio, setFechaInicio] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - 7);
    return d.toISOString().split("T")[0];
  });
  const [fechaFin, setFechaFin] = useState(() => {
    return new Date().toISOString().split("T")[0];
  });

  // Cargar dashboard en tiempo real (turnos de hoy)
  useEffect(() => {
    const cargarMonitoreo = async () => {
      try {
        setError(null);
        const data = await api.get("/api/monitoreo/turnos-hoy").then(r => r.data);
        setMonitoreo(data);
      } catch (err) {
        const backendError = err.response?.data?.error || err.message || "Error al cargar monitoreo de turnos";
        setError(backendError);
        console.error("Error al cargar monitoreo de turnos:", err);
      }
    };

    cargarMonitoreo();
    const intervalo = setInterval(cargarMonitoreo, 30000); // Recargar cada 30s
    return () => clearInterval(intervalo);
  }, []);

  // Cargar reportes históricos
  useEffect(() => {
    const cargarReportes = async () => {
      try {
        setError(null);
        const data = await api.get("/api/reportes/turnos", {
          params: {
            fecha_inicio: fechaInicio,
            fecha_fin: fechaFin,
          }
        }).then(r => r.data);
        setReportes(data);
      } catch (err) {
        const backendError = err.response?.data?.error || err.message || "Error al cargar reportes";
        setError(backendError);
        console.error("Error al cargar reportes:", err);
      } finally {
        setLoading(false);
      }
    };

    cargarReportes();
  }, [fechaInicio, fechaFin]);

  if (loading) {
    return (
      <Container className="mt-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Cargando...</span>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="mt-4">
      {error && <Alert variant="danger">{error}</Alert>}

      <Tabs defaultActiveKey="hoy" className="mb-4">
        {/* TAB 1: DASHBOARD EN TIEMPO REAL */}
        <Tab eventKey="hoy" title="📊 Dashboard - Hoy">
          {monitoreo && (
            <>
              <Row className="mb-4">
                <Col md={12}>
                  <h3>Monitoreo de Turnos - {monitoreo.fecha}</h3>
                  <p className="text-muted">
                    Actualización automática cada 30 segundos
                  </p>
                </Col>
              </Row>

              {/* Resumen Total */}
              <Row className="mb-4">
                <Col md={4}>
                  <Card className="text-center">
                    <Card.Body>
                      <h6 className="text-muted">Ventas Totales</h6>
                      <h3 className="text-primary">
                        {monitoreo.resumen_total.ventas}
                      </h3>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={4}>
                  <Card className="text-center">
                    <Card.Body>
                      <h6 className="text-muted">Dinero Total</h6>
                      <h3 className="text-success">
                        {money(monitoreo.resumen_total.dinero)}
                      </h3>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={4}>
                  <Card className="text-center">
                    <Card.Body>
                      <h6 className="text-muted">Promedio por Venta</h6>
                      <h3 className="text-info">
                        {money(monitoreo.resumen_total.promedio)}
                      </h3>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              {/* Turnos */}
              <Row>
                {monitoreo.turnos.map(turno => (
                  <Col md={4} key={turno.nombre} className="mb-4">
                    <Card
                      className="turno-card"
                      style={{
                        borderLeft: `5px solid ${TURNO_COLORS[turno.nombre]}`,
                      }}
                    >
                      <Card.Header
                        style={{
                          backgroundColor: TURNO_COLORS[turno.nombre],
                          color: "white",
                          fontWeight: "bold",
                        }}
                      >
                        {turno.label}
                      </Card.Header>
                      <Card.Body>
                        <Table size="sm" hover>
                          <tbody>
                            {turno.vendedores.length > 0 ? (
                              turno.vendedores.map(vendedor => (
                                <tr key={vendedor.id}>
                                  <td>
                                    <strong>{vendedor.nombre}</strong>
                                    <br />
                                    <small className="text-muted">
                                      {vendedor.ventas} venta{vendedor.ventas !== 1 ? "s" : ""}
                                    </small>
                                  </td>
                                  <td className="text-right">
                                    <strong>{money(vendedor.total)}</strong>
                                    <br />
                                    <small className="text-muted">
                                      {money(vendedor.promedio)} prom
                                    </small>
                                  </td>
                                </tr>
                              ))
                            ) : (
                              <tr>
                                <td colSpan="2" className="text-center text-muted">
                                  Sin ventas
                                </td>
                              </tr>
                            )}
                          </tbody>
                        </Table>

                        <hr />

                        <div className="text-center">
                          <p className="mb-2">
                            <strong>Total Turno:</strong> {turno.total_ventas} ventas
                          </p>
                          <h5 className="text-success">
                            {money(turno.total_dinero)}
                          </h5>
                          <small className="text-muted">
                            Promedio: {money(turno.promedio_venta)}
                          </small>
                        </div>
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>
            </>
          )}
        </Tab>

        {/* TAB 2: REPORTES HISTÓRICOS */}
        <Tab eventKey="reportes" title="📈 Reportes Históricos">
          <Row className="mb-4 mt-4">
            <Col md={3}>
              <label>Desde:</label>
              <input
                type="date"
                className="form-control"
                value={fechaInicio}
                onChange={e => setFechaInicio(e.target.value)}
              />
            </Col>
            <Col md={3}>
              <label>Hasta:</label>
              <input
                type="date"
                className="form-control"
                value={fechaFin}
                onChange={e => setFechaFin(e.target.value)}
              />
            </Col>
            <Col md={6} className="d-flex align-items-end">
              <Button
                variant="primary"
                onClick={() => {
                  // El efecto useEffect ya se ejecuta cuando cambian las fechas
                }}
              >
                Actualizar Reportes
              </Button>
            </Col>
          </Row>

          {reportes && (
            <>
              {/* Ranking de Vendedores */}
              <Row className="mb-4">
                <Col md={12}>
                  <Card>
                    <Card.Header className="bg-dark text-white">
                      <h5 className="mb-0">🏆 Ranking de Vendedores</h5>
                    </Card.Header>
                    <Card.Body>
                      <Table striped hover>
                        <thead>
                          <tr>
                            <th>Posición</th>
                            <th>Vendedor</th>
                            <th className="text-center">Ventas</th>
                            <th className="text-right">Total</th>
                            <th className="text-right">Promedio</th>
                          </tr>
                        </thead>
                        <tbody>
                          {reportes.ranking.map((vendedor, idx) => (
                            <tr key={vendedor.vendedor}>
                              <td>
                                <strong>#{idx + 1}</strong>
                              </td>
                              <td>{vendedor.vendedor}</td>
                              <td className="text-center">{vendedor.ventas}</td>
                              <td className="text-right text-success">
                                <strong>{money(vendedor.dinero)}</strong>
                              </td>
                              <td className="text-right">
                                {money(vendedor.promedio)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </Table>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              {/* Detalles de Reportes */}
              <Row>
                <Col md={12}>
                  <Card>
                    <Card.Header className="bg-info text-white">
                      <h5 className="mb-0">📋 Detalles de Ventas</h5>
                    </Card.Header>
                    <Card.Body>
                      <div style={{ maxHeight: "600px", overflowY: "auto" }}>
                        <Table striped hover size="sm">
                          <thead>
                            <tr>
                              <th>Fecha</th>
                              <th>Turno</th>
                              <th>Vendedor</th>
                              <th className="text-center">Productos</th>
                              <th className="text-right">Total</th>
                            </tr>
                          </thead>
                          <tbody>
                            {reportes.reportes.map(reporte => (
                              <tr key={reporte.venta_id}>
                                <td>{reporte.fecha}</td>
                                <td>
                                  <span
                                    className="badge"
                                    style={{
                                      backgroundColor:
                                        TURNO_COLORS[reporte.turno],
                                    }}
                                  >
                                    {reporte.turno}
                                  </span>
                                </td>
                                <td>{reporte.vendedor}</td>
                                <td className="text-center">
                                  {reporte.productos_vendidos}
                                </td>
                                <td className="text-right">
                                  {money(reporte.total_dinero)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </Table>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </>
          )}
        </Tab>
      </Tabs>
    </Container>
  );
}
