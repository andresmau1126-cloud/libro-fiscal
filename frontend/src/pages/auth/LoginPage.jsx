import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ nombre: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        await register(form.nombre, form.email, form.password);
      } else {
        await login(form.email, form.password);
      }
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <div className="icon-circle">
            <i className="bi bi-journal-bookmark-fill" style={{ fontSize: '1.8rem' }} />
          </div>
          <h2>Money Control</h2>
          <p>{isRegister ? 'Crear cuenta nueva' : 'Iniciar sesión'}</p>
        </div>

        <div className="login-body">
          {error && (
            <div className="alert alert-danger" style={{ borderRadius: 12, fontSize: '0.9rem' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {isRegister && (
              <div className="mb-3">
                <label className="form-label">Nombre</label>
                <input
                  type="text"
                  className="form-control"
                  value={form.nombre}
                  onChange={set('nombre')}
                  required
                  minLength={2}
                  maxLength={150}
                />
              </div>
            )}

            <div className="mb-3">
              <label className="form-label">Email</label>
              <input
                type="email"
                className="form-control"
                value={form.email}
                onChange={set('email')}
                required
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Contraseña</label>
              <input
                type="password"
                className="form-control"
                value={form.password}
                onChange={set('password')}
                required
                minLength={6}
              />
            </div>

            <button type="submit" className="btn-login" disabled={loading}>
              {loading ? 'Cargando...' : isRegister ? 'Registrarse' : 'Iniciar Sesión'}
            </button>
          </form>

          <div className="text-center mt-3">
            <span style={{ fontSize: '0.9rem', color: '#6b7280' }}>
              {isRegister ? '¿Ya tienes cuenta? ' : '¿No tienes cuenta? '}
            </span>
            <span
              style={{ color: 'var(--brand)', fontWeight: 600, cursor: 'pointer' }}
              onClick={() => { setIsRegister(!isRegister); setError(''); }}
            >
              {isRegister ? 'Iniciar Sesión' : 'Regístrate'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
