import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const { login, register, verifyRegistrationCode, resendRegistrationCode } = useAuth();
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ nombre: '', email: '', password: '' });
  const [verificationCode, setVerificationCode] = useState('');
  const [pendingVerificationEmail, setPendingVerificationEmail] = useState('');
  const [verificationEmail, setVerificationEmail] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);
    try {
      // Verificación de registro (código de seguridad)
      if (pendingVerificationEmail || isVerifying) {
        const email = pendingVerificationEmail || verificationEmail.trim().toLowerCase();
        const data = await verifyRegistrationCode(email, verificationCode);
        setMessage(data.message || 'Correo verificado correctamente.');
        setPendingVerificationEmail('');
        setVerificationEmail('');
        setIsVerifying(false);
        setVerificationCode('');
        navigate('/');
        return;
      }


      if (isRegister) {
        await register(form.nombre, form.email, form.password);
        setPendingVerificationEmail(form.email.trim().toLowerCase());
        setMessage('Registro exitoso. Revisa tu correo e ingresa el código de seguridad.');
        setVerificationCode('');
        setForm({ nombre: form.nombre, email: form.email, password: '' });
        return;
      }

      // Inicio de sesión normal con email + password
      await login(form.email, form.password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.message || err.message || 'Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    const email = pendingVerificationEmail || verificationEmail.trim().toLowerCase();
    if (!email) return;
    setError('');
    setMessage('');
    setLoading(true);
    try {
      const data = await resendRegistrationCode(email);
      setMessage(data.message || 'Se ha reenviado el código de verificación.');
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.message || err.message || 'Error de conexión');
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
          {message && (
            <div className="alert alert-success" style={{ borderRadius: 12, fontSize: '0.9rem' }}>
              {message}
            </div>
          )}
          {error && (
            <div className="alert alert-danger" style={{ borderRadius: 12, fontSize: '0.9rem' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {(pendingVerificationEmail || isVerifying) ? (
              <>
                <div className="mb-3">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-control"
                    value={pendingVerificationEmail || verificationEmail}
                    onChange={(e) => setVerificationEmail(e.target.value)}
                    disabled={Boolean(pendingVerificationEmail)}
                    required
                  />
                </div>
                <div className="mb-3">
                  <label className="form-label">Código de seguridad</label>
                  <input
                    type="text"
                    className="form-control"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value)}
                    required
                    minLength={6}
                    maxLength={6}
                  />
                </div>
              </>
            ) : (
              <>
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
              </>
            )}

            <button type="submit" className="btn-login" disabled={loading}>
              {loading
                ? 'Cargando...'
                : pendingVerificationEmail || isVerifying
                ? 'Verificar código'
                : isRegister
                ? 'Registrarse'
                : 'Iniciar Sesión'}
            </button>
          </form>

          {(pendingVerificationEmail || isVerifying) && (
            <div className="text-center mt-3">
              <button
                type="button"
                className="btn btn-link"
                onClick={handleResendCode}
                disabled={loading}
                style={{ paddingLeft: 0 }}
              >
                Reenviar código de verificación
              </button>
            </div>
          )}

          {isRegister && (
            <div className="text-center mt-3">
              <button
                type="button"
                className="btn btn-outline-primary"
                onClick={() => {
                  setIsRegister(false);
                  setIsVerifying(true);
                  setError('');
                  setMessage('');
                  setVerificationCode('');
                }}
                disabled={loading}
                style={{ fontWeight: 600 }}
              >
                Ya tengo código de verificación
              </button>
            </div>
          )}

          {!pendingVerificationEmail && !isRegister && (
            <div className="text-center mt-3">
              <button
                type="button"
                className="btn btn-outline-primary"
                onClick={() => {
                  setIsVerifying(!isVerifying);
                  setError('');
                  setMessage('');
                  setVerificationCode('');
                }}
                style={{ fontWeight: 600 }}
              >
                {isVerifying ? 'Volver al inicio de sesión' : 'Ya tengo código de verificación'}
              </button>
            </div>
          )}

          <div className="text-center mt-3">
            <span style={{ fontSize: '0.9rem', color: '#6b7280' }}>
              {isRegister ? '¿Ya tienes cuenta? ' : '¿No tienes cuenta? '}
            </span>
            <span
              style={{ color: 'var(--brand)', fontWeight: 600, cursor: 'pointer' }}
              onClick={() => {
                setIsRegister(!isRegister);
                setError('');
                setMessage('');
                setPendingVerificationEmail('');
                setVerificationCode('');
                setIsVerifying(false);
                setVerificationEmail('');
              }}
            >
              {isRegister ? 'Iniciar Sesión' : 'Regístrate'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
