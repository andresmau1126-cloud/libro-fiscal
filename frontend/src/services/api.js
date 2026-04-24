import axios from 'axios';

const envApiBase = import.meta.env.VITE_API_BASE_URL;
const isNativeApp = Boolean(window?.Capacitor?.isNativePlatform?.());
const fallbackApiBase = isNativeApp ? 'http://10.0.2.2:8000/api' : '/api';

const api = axios.create({
  baseURL: envApiBase || fallbackApiBase,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
});

// Redirect to login on 401 (except auth endpoints)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const url = err.config?.url || '';
    const isAuthEndpoint = url.includes('/auth/login') || url.includes('/auth/register') || url.includes('/auth/me');
    if (err.response?.status === 401 && !isAuthEndpoint) {
      window.location.href = '/login';
      // Return a forever-pending promise so callers never see the error
      return new Promise(() => {});
    }
    return Promise.reject(err);
  }
);

/* ── Auth ── */
export const authMe = () => api.get('/auth/me').then(r => r.data);
export const authLogin = (data) => api.post('/auth/login', data).then(r => r.data);
export const authRegister = (data) => api.post('/auth/register', data).then(r => r.data);
export const authLogout = () => api.post('/auth/logout').then(r => r.data);

/* ── Dashboard ── */
export const fetchDashboard = () => api.get('/dashboard').then(r => r.data);
export const fetchAuditoria = (limit = 100) => api.get(`/auditoria?limit=${limit}`).then(r => r.data);

/* ── Usuarios ── */
export const fetchUsuarios = () => api.get('/auth/usuarios/').then(r => r.data);
export const createUsuario = (data) => api.post('/auth/usuarios/', data).then(r => r.data);
export const updateUsuario = (id, data) => api.put(`/auth/usuarios/${id}`, data).then(r => r.data);
export const deleteUsuario = (id) => api.delete(`/auth/usuarios/${id}`).then(r => r.data);

/* ── Libros ── */
export const fetchLibros = () => api.get('/libros').then(r => r.data);
export const fetchLibro = (id) => api.get(`/libros/${id}`).then(r => r.data);
export const createLibro = (data) => api.post('/libros', data).then(r => r.data);
export const updateLibro = (id, data) => api.put(`/libros/${id}`, data).then(r => r.data);
export const deleteLibro = (id) => api.delete(`/libros/${id}`).then(r => r.data);

/* ── Movimientos ── */
export const fetchEntries = (libroId, year, month) =>
  api.get(`/entries?libro_id=${libroId}&year=${year}&month=${month}`).then(r => r.data);
export const createEntry = (data) => api.post('/entries', data).then(r => r.data);
export const updateEntry = (id, data) => api.put(`/entries/${id}`, data).then(r => r.data);
export const deleteEntry = (id) => api.delete(`/entries/${id}`).then(r => r.data);

/* ── Resumen ── */
export const fetchResumenAnual = (libroId, year) =>
  api.get(`/resumen-anual?libro_id=${libroId}&year=${year}`).then(r => r.data);

/* ── Export ── */
export const fetchExportBlob = (libroId, year, month) =>
  api.get(`/export?libro_id=${libroId}&year=${year}&month=${month}`, { responseType: 'blob' })
    .then(r => r.data);

export default api;
