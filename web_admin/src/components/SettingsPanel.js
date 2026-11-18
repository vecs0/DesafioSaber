import React, { useState, useEffect } from 'react';
import Modal from './Modal';

const API_BASE_URL = 'http://localhost:5000/api';

const SettingsPanel = () => {
  const [gameTitle, setGameTitle] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');
  const [config, setConfig] = useState({});
  const [adminPassword, setAdminPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [users, setUsers] = useState([]);
  const [newUser, setNewUser] = useState({ fullName: '', username: '', password: '', image: null });
  const [isUserModalOpen, setIsUserModalOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [showNewUserPassword, setShowNewUserPassword] = useState(false);
  const [showEditUserPassword, setShowEditUserPassword] = useState(false);
  const [newUserImagePreview, setNewUserImagePreview] = useState(null);
  const [editUserImagePreview, setEditUserImagePreview] = useState(null);
  const [admins, setAdmins] = useState([]);

  useEffect(() => {
    loadConfig();
    loadAdminUsers();
    // Cargar jugadores después de un breve delay para asegurar que loadAdminUsers termine
    setTimeout(() => {
      loadPlayers();
    }, 500);
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/config`);
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
        setGameTitle(data.title || '');
      } else {
        setError('Error al cargar la configuración');
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const loadAdminUsers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin-users`);
      if (response.ok) {
        const data = await response.json();
        setAdmins(data.users || []);
      } else {
        setError('Error al cargar administradores');
      }
    } catch (error) {
      setError('Error de conexión al cargar administradores: ' + error.message);
    }
  };

  const loadPlayers = async () => {
    try {
      console.log('Cargando jugadores para configuración...');
      const response = await fetch(`${API_BASE_URL}/players`);
      if (response.ok) {
        const data = await response.json();
        console.log('Jugadores cargados:', data);
        // Combinar usuarios admin con jugadores para gestión completa
        const allUsers = [...admins, ...data];
        console.log('Todos los usuarios:', allUsers);
        setUsers(allUsers);
      } else {
        console.error('Error cargando jugadores:', response.status);
      }
    } catch (error) {
      console.error('Error cargando jugadores:', error);
    }
  };

  const saveConfig = async () => {
    try {
      setLoading(true);
      const newConfig = { ...config, title: gameTitle };
      const response = await fetch(`${API_BASE_URL}/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig)
      });
      if (response.ok) {
        setMessage('Configuración guardada correctamente.');
        setConfig(newConfig);
        // Notificar cambio para sincronización en tiempo real
        console.log('Configuración actualizada:', newConfig);
      } else {
        setMessage('Error al guardar la configuración.');
      }
    } catch (error) {
      setMessage('Error de conexión al guardar configuración.');
    } finally {
      setLoading(false);
    }
  };

  const updateAdminPassword = () => {
    if (adminPassword === confirmPassword && adminPassword.length >= 6) {
      setMessage('Contraseña de administrador actualizada con éxito.');
      setAdminPassword('');
      setConfirmPassword('');
    } else {
      setMessage('Las contraseñas no coinciden o son demasiado cortas.');
    }
  };

  const addUser = async () => {
    if (!newUser.fullName || !newUser.username || !newUser.password) {
      setMessage('Por favor, completa todos los campos del nuevo usuario.');
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/admin-users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newUser)
      });
      if (response.ok) {
        const data = await response.json();
        if (newUser.image) {
          const formData = new FormData();
          formData.append('image', newUser.image);
          await fetch(`${API_BASE_URL}/admin-users/${data.user.id}/image`, {
            method: 'POST',
            body: formData
          });
        }
        // Recargar lista de admins para evitar duplicados
        await loadAdminUsers();
        setNewUser({ fullName: '', username: '', password: '', image: null });
        setNewUserImagePreview(null);
        setMessage('Usuario agregado con éxito.');
      } else {
        const errorData = await response.json();
        setMessage(errorData.error || 'Error al agregar usuario.');
      }
    } catch (error) {
      setMessage('Error de conexión al agregar usuario.');
    }
  };

  const deleteUser = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin-users/${id}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        // Recargar lista de admins para reflejar cambios
        await loadAdminUsers();
        setMessage('Usuario eliminado.');
      } else {
        const errorData = await response.json();
        setMessage(errorData.error || 'Error al eliminar usuario.');
      }
    } catch (error) {
      setMessage('Error de conexión al eliminar usuario.');
    }
  };

  const openEditUserModal = (user) => {
    setCurrentUser({ ...user });
    setIsUserModalOpen(true);
  };

  const saveUserChanges = async () => {
    if (!currentUser.fullName || !currentUser.username) {
      setMessage('Por favor, completa todos los campos.');
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/admin-users/${currentUser.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentUser)
      });
      if (response.ok) {
        if (currentUser.image && currentUser.image instanceof File) {
          const formData = new FormData();
          formData.append('image', currentUser.image);
          await fetch(`${API_BASE_URL}/admin-users/${currentUser.id}/image`, {
            method: 'POST',
            body: formData
          });
        }
        setUsers(users.map(u => u.id === currentUser.id ? currentUser : u));
        setIsUserModalOpen(false);
        setCurrentUser(null);
        setEditUserImagePreview(null);
        setMessage('Usuario actualizado con éxito.');
      } else {
        setMessage('Error al actualizar usuario.');
      }
    } catch (error) {
      setMessage('Error de conexión al actualizar usuario.');
    }
  };

  const handleNewUserChange = (e) => {
    setNewUser({ ...newUser, [e.target.name]: e.target.value });
  };

  const handleModalUserChange = (e) => {
    setCurrentUser({ ...currentUser, [e.target.name]: e.target.value });
  };

  const handleSaveAllChanges = () => {
    alert('¡Cambios en configuración guardados! (Simulado)');
    // Aquí iría la lógica para enviar los cambios a la base de datos real
  };

  if (loading) {
    return <div className="p-6 bg-white rounded-xl shadow-lg m-6">Cargando configuración...</div>;
  }
  if (error) {
    return <div className="p-6 bg-white rounded-xl shadow-lg m-6 text-red-600">{error}</div>;
  }

  return (
    <div className="p-6 bg-white rounded-xl shadow-lg m-6">
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-blue-700">Configuración del Sistema</h2>
        <span className="text-lg font-semibold text-blue-900 bg-blue-100 px-4 py-2 rounded-full shadow">DesafíoSaber v2.0.1</span>
      </div>
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Configuración del Juego</h2>

      <div className="mb-8 p-6 border border-gray-200 rounded-xl bg-gray-50">
        <h3 className="text-xl font-semibold mb-4 text-gray-700">Título del Juego</h3>
        <div className="flex gap-3">
          <input
            type="text"
            value={gameTitle}
            onChange={(e) => setGameTitle(e.target.value)}
            placeholder="Ingresa el título del juego"
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <button 
            onClick={saveConfig}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Guardar Título
          </button>
        </div>
        <p className="text-sm text-gray-500 mt-2">Este título se mostrará en el juego y se actualizará en tiempo real.</p>
        {message && <p className="mt-2 text-sm text-green-600">{message}</p>}
      </div>

      <div className="p-6 border border-gray-200 rounded-xl bg-gray-50 mb-8">
        <h3 className="text-xl font-semibold mb-4 text-gray-700">Seguridad de Administrador</h3>
        <input
          type="password"
          value={adminPassword}
          onChange={(e) => setAdminPassword(e.target.value)}
          placeholder="Nueva Contraseña"
          className="w-full p-3 border border-gray-300 rounded-lg mb-3 focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Confirmar Contraseña"
          className="w-full p-3 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-blue-500"
        />
        <button onClick={updateAdminPassword} className="w-full py-3 bg-green-600 text-white rounded-lg shadow-md hover:bg-green-700 transition-colors">
          Actualizar Contraseña
        </button>
        {message && <p className="mt-4 text-center text-sm text-gray-600">{message}</p>}
      </div>

      <div className="p-6 border border-gray-200 rounded-xl bg-gray-50 mb-8">
        <h3 className="text-xl font-semibold mb-4 text-gray-700">Gestión de Usuarios Administradores</h3>
        <div className="mb-6 p-4 border border-gray-300 rounded-lg bg-white">
          <h4 className="text-lg font-semibold mb-3">Agregar Nuevo Usuario</h4>
          <div className="mb-3">
            <label className="block text-gray-700 text-sm font-bold mb-2">Nombre Completo:</label>
            <input
              type="text"
              name="fullName"
              value={newUser.fullName}
              onChange={handleNewUserChange}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Ej. Juan Pérez"
            />
          </div>
          <div className="mb-3">
            <label className="block text-gray-700 text-sm font-bold mb-2">Usuario:</label>
            <input
              type="text"
              name="username"
              value={newUser.username}
              onChange={handleNewUserChange}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="usuario123"
            />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Contraseña:</label>
            <div className="relative">
              <input
                type={showNewUserPassword ? 'text' : 'password'}
                name="password"
                value={newUser.password}
                onChange={handleNewUserChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 pr-10"
                placeholder=""
              />
              <button
                type="button"
                onClick={() => setShowNewUserPassword(v => !v)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 focus:outline-none"
                tabIndex={-1}
                aria-label={showNewUserPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {showNewUserPassword ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-5.523 0-10-4.477-10-10a9.96 9.96 0 012.197-6.197m1.414-1.414A9.96 9.96 0 0112 3c5.523 0 10 4.477 10 10a9.96 9.96 0 01-1.197 4.197m-1.414 1.414A9.96 9.96 0 0112 21c-1.05 0-2.07-.162-3.025-.462M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0zm-9.197 4.197A9.96 9.96 0 012 12c0-5.523 4.477-10 10-10s10 4.477 10 10a9.96 9.96 0 01-1.197 4.197m-1.414 1.414A9.96 9.96 0 0112 21c-1.05 0-2.07-.162-3.025-.462" /></svg>
                )}
              </button>
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Imagen de Perfil (JPG/PNG, máx 1MB):</label>
            <input
              type="file"
              accept="image/png, image/jpeg"
              onChange={e => {
                const file = e.target.files[0];
                if (file) {
                  if (file.size > 1024 * 1024) {
                    setMessage('La imagen supera el tamaño máximo de 1MB');
                    return;
                  }
                  setNewUser({ ...newUser, image: file });
                  setNewUserImagePreview(URL.createObjectURL(file));
                }
              }}
              className="w-full p-2 border border-gray-300 rounded-lg"
            />
            {newUserImagePreview && <img src={newUserImagePreview} alt="Previsualización" className="mt-2 w-20 h-20 rounded-full object-cover border" />}
          </div>
          <button onClick={addUser} className="w-full py-2 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 transition-colors">Agregar Usuario</button>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full bg-white rounded-xl shadow-sm">
            <thead>
              <tr className="bg-gray-100 border-b border-gray-200 text-gray-600 uppercase text-sm leading-normal">
                <th className="py-3 px-6 text-left">Nombre Completo</th>
                <th className="py-3 px-6 text-left">Usuario</th>
                <th className="py-3 px-6 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody className="text-gray-700 text-sm font-light">
              {admins.map((user) => (
                <tr key={user.id} className={`border-b border-gray-200 hover:bg-gray-50 ${user.id === '1' || user.id === 1 ? 'bg-yellow-100 font-bold' : ''}`}>
                  <td className="py-3 px-6 text-left whitespace-nowrap">{user.fullName}{(user.id === '1' || user.id === 1) && ' (Admin Principal)'}</td>
                  <td className="py-3 px-6 text-left">{user.username}</td>
                  <td className="py-3 px-6 text-center">
                    <button onClick={() => openEditUserModal(user)} className="bg-blue-500 text-white py-1 px-3 rounded-md hover:bg-blue-600 transition-colors mr-2">Editar</button>
                    {!(user.id === '1' || user.id === 1) && (
                    <button onClick={() => deleteUser(user.id)} className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600 transition-colors">Eliminar</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="p-6 border border-gray-200 rounded-xl bg-gray-50">
        <h3 className="text-xl font-semibold mb-4 text-gray-700">Gestión de Datos del Juego</h3>
        <p className="text-gray-600 mb-4">Aquí puedes gestionar la base de datos de tu juego. ¡Cuidado con lo que haces, mi chavo!</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button className="py-3 bg-purple-600 text-white rounded-lg shadow-md hover:bg-purple-700 transition-colors">
            Exportar Datos (JSON)
          </button>
          <button className="py-3 bg-orange-600 text-white rounded-lg shadow-md hover:bg-orange-700 transition-colors">
            Importar Datos (JSON)
          </button>
          <button className="py-3 bg-red-600 text-white rounded-lg shadow-md hover:bg-red-700 transition-colors">
            Limpiar Datos de Jugadores
          </button>
          <button className="py-3 bg-red-600 text-white rounded-lg shadow-md hover:bg-red-700 transition-colors">
            Restablecer Preguntas por Defecto
          </button>
        </div>
      </div>

      <button onClick={handleSaveAllChanges} className="w-full mt-6 py-3 bg-green-600 text-white rounded-lg shadow-md hover:bg-green-700 transition-colors">
        Guardar Todos los Cambios en Configuración
      </button>

      {isUserModalOpen && currentUser && (
        <Modal onClose={() => setIsUserModalOpen(false)}>
          <h3 className="text-xl font-bold mb-4">Editar Usuario Administrador</h3>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Nombre Completo:</label>
            <input type="text" name="fullName" value={currentUser.fullName} onChange={handleModalUserChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Usuario:</label>
            <input type="text" name="username" value={currentUser.username} onChange={handleModalUserChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Contraseña:</label>
            <div className="relative">
              <input
                type={showEditUserPassword ? 'text' : 'password'}
                name="password"
                value={currentUser.password || ''}
                placeholder="Dejar vacío para no cambiarla"
                onChange={handleModalUserChange}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 pr-10"
              />
              <button
                type="button"
                onClick={() => setShowEditUserPassword(v => !v)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 focus:outline-none"
                tabIndex={-1}
                aria-label={showEditUserPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {showEditUserPassword ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-5.523 0-10-4.477-10-10a9.96 9.96 0 012.197-6.197m1.414-1.414A9.96 9.96 0 0112 3c5.523 0 10 4.477 10 10a9.96 9.96 0 01-1.197 4.197m-1.414 1.414A9.96 9.96 0 0112 21c-1.05 0-2.07-.162-3.025-.462M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0zm-9.197 4.197A9.96 9.96 0 012 12c0-5.523 4.477-10 10-10s10 4.477 10 10a9.96 9.96 0 01-1.197 4.197m-1.414 1.414A9.96 9.96 0 0112 21c-1.05 0-2.07-.162-3.025-.462" /></svg>
                )}
              </button>
            </div>
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2">Imagen de Perfil (JPG/PNG, máx 1MB):</label>
            <input
              type="file"
              accept="image/png, image/jpeg"
              onChange={e => {
                const file = e.target.files[0];
                if (file) {
                  if (file.size > 1024 * 1024) {
                    setMessage('La imagen supera el tamaño máximo de 1MB');
                    return;
                  }
                  setCurrentUser({ ...currentUser, image: file });
                  setEditUserImagePreview(URL.createObjectURL(file));
                }
              }}
              className="w-full p-2 border border-gray-300 rounded-lg"
            />
            {(editUserImagePreview || currentUser?.image) && <img src={editUserImagePreview || currentUser.image} alt="Previsualización" className="mt-2 w-20 h-20 rounded-full object-cover border" />}
          </div>
          <button onClick={saveUserChanges} className="w-full py-2 bg-green-600 text-white rounded-lg shadow-md hover:bg-green-700 transition-colors">Guardar Cambios</button>
        </Modal>
      )}

      <button onClick={saveConfig} className="w-full mt-6 py-3 bg-green-600 text-white rounded-lg shadow-md hover:bg-green-700 transition-colors">
        Guardar Cambios en Configuración
      </button>
      {message && <div className="mt-4 text-green-600">{message}</div>}
    </div>
  );
};

export default SettingsPanel;