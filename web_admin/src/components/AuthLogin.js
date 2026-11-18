import React, { useState, useEffect } from 'react';
import Modal from './Modal';

const AuthLogin = ({ onLogin, showAdminNameInput }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [adminNameInput, setAdminNameInput] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [showRecoveryModal, setShowRecoveryModal] = useState(false);
  const [recoveryEnabled, setRecoveryEnabled] = useState(false);
  const [recoveryPassword, setRecoveryPassword] = useState('');
  const [recoveryMessage, setRecoveryMessage] = useState('');

  useEffect(() => {
    // Consultar si el modo recuperación está habilitado
    fetch('http://localhost:5000/api/admin-recovery', { method: 'POST', body: JSON.stringify({ password: 'check' }), headers: { 'Content-Type': 'application/json' } })
      .then(res => res.status === 403 ? setRecoveryEnabled(true) : setRecoveryEnabled(false))
      .catch(() => setRecoveryEnabled(false));
  }, []);

  const handleLogin = async () => {
    let res;
    try {
      res = await fetch('http://localhost:5000/api/admin-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, fullName: adminNameInput, password }),
      });
    } catch {
      setError('Error de conexión con el servidor.');
      return;
    }
    const data = await res.json().catch(() => ({}));
    const user = res.ok && data.success ? data.user : null;
    if (user) {
      setError('');
      onLogin(user.fullName, user.username);
    } else {
      setError('Usuario o contraseña incorrectos. Recuerda que el nombre y usuario deben coincidir exactamente con el registrado (mayúsculas, tildes y espacios incluidos).');
    }
  };

  // URL de imagen de paisaje profesional libre
  const landscapeUrl = 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1500&q=80';

  return (
    <>
      {/* Fondo de paisaje con overlay oscuro y desenfoque */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: -2,
        background: `url(${landscapeUrl}) center center / cover no-repeat`,
        filter: 'blur(2px) brightness(0.6)',
        transition: 'filter 0.5s',
      }} />
      {/* Overlay para glassmorphism */}
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: -1,
        background: 'rgba(30, 41, 59, 0.3)',
        backdropFilter: 'blur(2px)',
      }} />
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white bg-opacity-20 backdrop-blur-lg border border-white border-opacity-30 shadow-2xl w-full max-w-md rounded-2xl p-10" style={{boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)'}}>
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2 drop-shadow">DesafíoSaber Admin</h1>
          </div>
          {showAdminNameInput && (
            <div className="mb-6">
              <label className="block text-white text-sm font-bold mb-2" htmlFor="adminName">
                Tu Nombre de Administrador
              </label>
              <div className="relative">
                <input
                  type="text"
                  id="adminName"
                  value={adminNameInput}
                  onChange={(e) => setAdminNameInput(e.target.value)}
                  className="shadow appearance-none border rounded-lg w-full py-3 px-4 pl-10 text-gray-800 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all bg-white bg-opacity-70"
                  placeholder=""
                  autoComplete="off"
                />
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                  <svg xmlns='http://www.w3.org/2000/svg' className='h-5 w-5' fill='none' viewBox='0 0 24 24' stroke='currentColor'><path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M5.121 17.804A13.937 13.937 0 0112 15c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0z' /></svg>
                </span>
              </div>
            </div>
          )}
          <div className="mb-6">
            <label className="block text-white text-sm font-bold mb-2" htmlFor="username">
              Usuario
            </label>
            <div className="relative">
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="shadow appearance-none border rounded-lg w-full py-3 px-4 pl-10 text-gray-800 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all bg-white bg-opacity-70"
                placeholder=""
                autoComplete="off"
                onKeyDown={(e) => { if (e.key === 'Enter') handleLogin(); }}
              />
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                <svg xmlns='http://www.w3.org/2000/svg' className='h-5 w-5' fill='none' viewBox='0 0 24 24' stroke='currentColor'><path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M5.121 17.804A13.937 13.937 0 0112 15c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0z' /></svg>
              </span>
            </div>
          </div>
          <div className="mb-6">
            <label className="block text-white text-sm font-bold mb-2" htmlFor="password">
              Contraseña
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="shadow appearance-none border rounded-lg w-full py-3 px-4 pl-10 text-gray-800 mb-3 leading-tight focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all pr-10 bg-white bg-opacity-70"
                placeholder=""
                autoComplete="off"
                onKeyDown={(e) => { if (e.key === 'Enter') handleLogin(); }}
              />
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                <svg xmlns='http://www.w3.org/2000/svg' className='h-5 w-5' fill='none' viewBox='0 0 24 24' stroke='currentColor'><path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M12 11c1.104 0 2-.896 2-2s-.896-2-2-2-2 .896-2 2 .896 2 2 2zm0 2c-2.21 0-4 1.79-4 4v1h8v-1c0-2.21-1.79-4-4-4z' /></svg>
              </span>
              <button
                type="button"
                onClick={() => setShowPassword(v => !v)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 focus:outline-none"
                tabIndex={-1}
                aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {showPassword ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-5.523 0-10-4.477-10-10a9.96 9.96 0 012.197-6.197m1.414-1.414A9.96 9.96 0 0112 3c5.523 0 10 4.477 10 10a9.96 9.96 0 01-1.197 4.197m-1.414 1.414A9.96 9.96 0 0112 21c-1.05 0-2.07-.162-3.025-.462M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0zm-9.197 4.197A9.96 9.96 0 012 12c0-5.523 4.477-10 10-10s10 4.477 10 10a9.96 9.96 0 01-1.197 4.197m-1.414 1.414A9.96 9.96 0 0112 21c-1.05 0-2.07-.162-3.025-.462" /></svg>
                )}
              </button>
            </div>
          </div>
          {error && <p className="text-red-500 text-xs italic mb-4 text-center">{error}</p>}
          <button
            onClick={handleLogin}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:shadow-outline transition-all duration-200 transform hover:scale-100 shadow-lg"
          >
            Iniciar Sesión
          </button>
          <div className="mt-4 text-center">
            <button
              type="button"
              className="text-sm text-blue-200 hover:text-white underline transition-colors"
              onClick={() => setShowForgotModal(true)}
            >
              ¿Olvidaste tu contraseña?
            </button>
          </div>
          {showForgotModal && (
            <Modal onClose={() => setShowForgotModal(false)}>
              <div className="p-6 bg-white bg-opacity-80 rounded-xl shadow-xl backdrop-blur-md">
                <h2 className="text-xl font-bold mb-4 text-gray-800">Recuperar Contraseña</h2>
                <p className="text-gray-700 mb-4">
                  Por seguridad, la contraseña solo puede ser restablecida por otro administrador desde el panel de configuración.<br/>
                  Si eres el único administrador, contacta con el soporte o sigue las instrucciones del manual para restablecer la contraseña.
                </p>
                {recoveryEnabled && (
                  <div className="mt-4 text-center">
                    <button
                      type="button"
                      className="text-sm text-yellow-700 hover:text-blue-700 underline transition-colors font-semibold"
                      onClick={() => { setShowForgotModal(false); setShowRecoveryModal(true); }}
                    >
                      Recuperar acceso como único administrador
                    </button>
                  </div>
                )}
                <button
                  onClick={() => setShowForgotModal(false)}
                  className="w-full py-2 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 transition-colors mt-6"
                >
                  Cerrar
                </button>
              </div>
            </Modal>
          )}
          {showRecoveryModal && (
            <Modal onClose={() => setShowRecoveryModal(false)}>
              <div className="p-6">
                <h2 className="text-xl font-bold mb-4 text-gray-800">Recuperación de Acceso</h2>
                <p className="text-gray-700 mb-4">
                  Se ha detectado el modo recuperación. Ingresa una nueva contraseña para el administrador principal.<br/>
                  (Este proceso solo está disponible si tienes acceso físico o remoto al servidor)
                </p>
                <input
                  type="password"
                  value={recoveryPassword}
                  onChange={e => setRecoveryPassword(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 mb-4"
                  placeholder="Nueva contraseña"
                />
                <button
                  onClick={async () => {
                    setRecoveryMessage('');
                    const res = await fetch('http://localhost:5000/api/admin-recovery', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ password: recoveryPassword })
                    });
                    const data = await res.json();
                    if (data.success) {
                      setRecoveryMessage('Contraseña restablecida correctamente. Ahora puedes iniciar sesión.');
                    } else {
                      setRecoveryMessage(data.error || 'Error al restablecer la contraseña');
                    }
                  }}
                  className="w-full py-2 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 transition-colors mb-2"
                >
                  Restablecer Contraseña
                </button>
                {recoveryMessage && <div className="text-center text-green-600 mt-2">{recoveryMessage}</div>}
                <button
                  onClick={() => setShowRecoveryModal(false)}
                  className="w-full py-2 bg-gray-300 text-gray-800 rounded-lg shadow-md hover:bg-gray-400 transition-colors mt-2"
                >
                  Cerrar
                </button>
              </div>
            </Modal>
          )}
        </div>
      </div>
    </>
  );
};

export default AuthLogin;