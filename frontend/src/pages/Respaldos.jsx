import React, { useState, useEffect } from 'react';
import './Respaldos.css';
import { API_BASE_URL } from '../services/api';

const Respaldos = () => {
  const [respaldos, setRespaldos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    tipo: 'completo'
  });
  const [crearLoading, setCrearLoading] = useState(false);
  const [estadisticas, setEstadisticas] = useState(null);
  const [filtroTipo, setFiltroTipo] = useState('todos');
  const [filtroEstado, setFiltroEstado] = useState('todos');

  // Cargar respaldos
  useEffect(() => {
    cargarRespaldos();
    cargarEstadisticas();
  }, []);

  const cargarRespaldos = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/respaldos/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      
      if (!response.ok) throw new Error('Error al cargar respaldos');
      
      const data = await response.json();
      setRespaldos(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const cargarEstadisticas = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/respaldos/estadisticas/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setEstadisticas(data);
      }
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const crearRespaldo = async (e) => {
    e.preventDefault();
    
    try {
      setCrearLoading(true);
      const token = localStorage.getItem('access_token');
      
      // Usar nombre actual si no se proporcionó
      const nombre = formData.nombre || `Respaldo ${new Date().toLocaleString()}`;
      
      const response = await fetch(`${API_BASE_URL}/respaldos/crear_respaldo/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          nombre,
          descripcion: formData.descripcion,
          tipo: formData.tipo
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al crear respaldo');
      }
      
      const data = await response.json();
      setShowForm(false);
      setFormData({
        nombre: '',
        descripcion: '',
        tipo: 'completo'
      });
      
      // Recargar respaldos
      await cargarRespaldos();
      await cargarEstadisticas();
      
      // Mostrar notificación de éxito
      alert('Respaldo creado exitosamente');
    } catch (err) {
      alert(`Error: ${err.message}`);
      console.error('Error:', err);
    } finally {
      setCrearLoading(false);
    }
  };

  const restaurarRespaldo = async (id, nombre) => {
    if (!window.confirm(`¿Está seguro de que desea restaurar el respaldo "${nombre}"? Esta acción no puede deshacerse.`)) {
      return;
    }
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/respaldos/${id}/restaurar/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          notas: `Restauración manual realizada por el usuario`
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error al restaurar respaldo');
      }
      
      const data = await response.json();
      
      // Recargar respaldos
      await cargarRespaldos();
      await cargarEstadisticas();
      
      alert(`Respaldo restaurado exitosamente en ${data.duracion_segundos?.toFixed(2)}s`);
    } catch (err) {
      alert(`Error: ${err.message}`);
      console.error('Error:', err);
    }
  };

  const descargarRespaldo = async (id, nombre) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/respaldos/${id}/descargar/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      
      if (!response.ok) throw new Error('Error al descargar respaldo');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${nombre.replace(/ /g, '_')}.sql`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert(`Error: ${err.message}`);
      console.error('Error:', err);
    }
  };

  const eliminarRespaldo = async (id, nombre) => {
    if (!window.confirm(`¿Está seguro de que desea eliminar el respaldo "${nombre}"?`)) {
      return;
    }
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/respaldos/${id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      
      if (!response.ok) throw new Error('Error al eliminar respaldo');
      
      await cargarRespaldos();
      await cargarEstadisticas();
      
      alert('Respaldo eliminado exitosamente');
    } catch (err) {
      alert(`Error: ${err.message}`);
      console.error('Error:', err);
    }
  };

  const formatearFecha = (fecha) => {
    return new Date(fecha).toLocaleString('es-ES');
  };

  const formatearTamano = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Filtrar respaldos
  const respaldosFiltrados = respaldos.filter(r => {
    if (filtroTipo !== 'todos' && r.tipo !== filtroTipo) return false;
    if (filtroEstado !== 'todos' && r.estado !== filtroEstado) return false;
    return true;
  });

  return (
    <div className="respaldos-container">
      <div className="respaldos-header">
        <h1>📋 Copias de Seguridad</h1>
        <p className="subtitle">Gestiona tus puntos de control y restauraciones</p>
      </div>

      {/* Estadísticas */}
      {estadisticas && (
        <div className="estadisticas-grid">
          <div className="stat-card">
            <div className="stat-icon">📦</div>
            <div className="stat-info">
              <div className="stat-number">{estadisticas.total_respaldos}</div>
              <div className="stat-label">Total de Respaldos</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-info">
              <div className="stat-number">{estadisticas.respaldos_completados}</div>
              <div className="stat-label">Completados</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">❌</div>
            <div className="stat-info">
              <div className="stat-number">{estadisticas.respaldos_fallidos}</div>
              <div className="stat-label">Fallidos</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">💾</div>
            <div className="stat-info">
              <div className="stat-number">{formatearTamano(estadisticas.tamano_total)}</div>
              <div className="stat-label">Espacio Utilizado</div>
            </div>
          </div>
        </div>
      )}

      {/* Botones de acción */}
      <div className="actions-bar">
        <button 
          className="btn btn-primary"
          onClick={() => setShowForm(!showForm)}
        >
          + Crear Nuevo Respaldo
        </button>
        <button 
          className="btn btn-secondary"
          onClick={cargarRespaldos}
        >
          🔄 Actualizar
        </button>
      </div>

      {/* Formulario de crear respaldo */}
      {showForm && (
        <div className="form-container">
          <h3>Crear Nuevo Respaldo</h3>
          <form onSubmit={crearRespaldo}>
            <div className="form-group">
              <label htmlFor="nombre">Nombre del Respaldo:</label>
              <input
                type="text"
                id="nombre"
                name="nombre"
                placeholder="Ej: Respaldo fin de mes"
                value={formData.nombre}
                onChange={handleInputChange}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="descripcion">Descripción (opcional):</label>
              <textarea
                id="descripcion"
                name="descripcion"
                placeholder="Descripción del respaldo..."
                rows="3"
                value={formData.descripcion}
                onChange={handleInputChange}
              ></textarea>
            </div>
            
            <div className="form-group">
              <label htmlFor="tipo">Tipo de Respaldo:</label>
              <select
                id="tipo"
                name="tipo"
                value={formData.tipo}
                onChange={handleInputChange}
              >
                <option value="completo">Completo (Base de datos + Configuración)</option>
                <option value="base_datos">Solo Base de Datos</option>
                <option value="configuracion">Solo Configuración</option>
              </select>
            </div>
            
            <div className="form-actions">
              <button 
                type="submit" 
                className="btn btn-success"
                disabled={crearLoading}
              >
                {crearLoading ? 'Creando...' : '✓ Crear Respaldo'}
              </button>
              <button 
                type="button"
                className="btn btn-cancel"
                onClick={() => setShowForm(false)}
                disabled={crearLoading}
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filtros */}
      <div className="filters-bar">
        <div className="filter-group">
          <label htmlFor="filtroTipo">Tipo:</label>
          <select 
            id="filtroTipo"
            value={filtroTipo}
            onChange={(e) => setFiltroTipo(e.target.value)}
          >
            <option value="todos">Todos</option>
            <option value="completo">Completo</option>
            <option value="base_datos">Base de Datos</option>
            <option value="configuracion">Configuración</option>
          </select>
        </div>
        
        <div className="filter-group">
          <label htmlFor="filtroEstado">Estado:</label>
          <select 
            id="filtroEstado"
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
          >
            <option value="todos">Todos</option>
            <option value="completado">Completado</option>
            <option value="en_proceso">En Proceso</option>
            <option value="fallido">Fallido</option>
          </select>
        </div>
      </div>

      {/* Tabla de respaldos */}
      {loading ? (
        <div className="loading">Cargando respaldos...</div>
      ) : error ? (
        <div className="error-message">Error: {error}</div>
      ) : respaldosFiltrados.length === 0 ? (
        <div className="empty-state">
          <p>📭 No hay respaldos disponibles</p>
          <small>Crea tu primer respaldo haciendo clic en "Crear Nuevo Respaldo"</small>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="respaldos-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Tipo</th>
                <th>Estado</th>
                <th>Fecha Creación</th>
                <th>Tamaño</th>
                <th>Creado por</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {respaldosFiltrados.map(respaldo => (
                <tr key={respaldo.id} className={`estado-${respaldo.estado}`}>
                  <td className="nombre-cell">
                    <strong>{respaldo.nombre}</strong>
                    {respaldo.descripcion && (
                      <small>{respaldo.descripcion}</small>
                    )}
                  </td>
                  <td>
                    <span className={`badge badge-tipo-${respaldo.tipo}`}>
                      {respaldo.tipo_display}
                    </span>
                  </td>
                  <td>
                    <span className={`badge badge-estado-${respaldo.estado}`}>
                      {respaldo.estado_display}
                    </span>
                  </td>
                  <td className="fecha">{formatearFecha(respaldo.fecha_creacion)}</td>
                  <td className="tamano">{formatearTamano(respaldo.tamano_archivo)}</td>
                  <td className="usuario">{respaldo.usuario_creador_nombre || '-'}</td>
                  <td className="acciones">
                    <div className="button-group">
                      {respaldo.estado === 'completado' && (
                        <>
                          <button
                            className="btn-accion btn-restaurar"
                            title="Restaurar respaldo"
                            onClick={() => restaurarRespaldo(respaldo.id, respaldo.nombre)}
                          >
                            🔄
                          </button>
                          <button
                            className="btn-accion btn-descargar"
                            title="Descargar respaldo"
                            onClick={() => descargarRespaldo(respaldo.id, respaldo.nombre)}
                          >
                            ⬇️
                          </button>
                        </>
                      )}
                      <button
                        className="btn-accion btn-eliminar"
                        title="Eliminar respaldo"
                        onClick={() => eliminarRespaldo(respaldo.id, respaldo.nombre)}
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Información adicional */}
      <div className="info-panel">
        <h4>ℹ️ Información Importante</h4>
        <ul>
          <li>Los respaldos se almacenan en el servidor y pueden ocupar espacio</li>
          <li>Antes de restaurar un respaldo, se crea automáticamente una copia de seguridad de la base de datos actual</li>
          <li>La restauración sobrescribirá toda la información actual con la del respaldo</li>
          <li>Descargar un respaldo permite guardar una copia en tu computadora</li>
        </ul>
      </div>
    </div>
  );
};

export default Respaldos;
