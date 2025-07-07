import React, { useState, useEffect } from 'react';
import Modal from './Modal';

const API_BASE_URL = 'http://localhost:5000/api';

const PlayersManagement = () => {
  const [players, setPlayers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentPlayer, setCurrentPlayer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newPlayer, setNewPlayer] = useState({ username: '', score: 0, mode: '', categoria: '', correctas: 0, incorrectas: 0, tiempo: 0 });

  useEffect(() => {
    loadPlayers();
  }, []);

  const loadPlayers = async () => {
    try {
      setLoading(true);
      console.log('Cargando jugadores...');
      const response = await fetch(`${API_BASE_URL}/players`);
      console.log('Respuesta del servidor:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Datos recibidos:', data);
        
        // Asegurar que todos los jugadores tengan los campos necesarios
        const formattedPlayers = data.map(player => ({
          id: player.id || '',
          username: player.username || '',
          fullName: player.fullName || '',
          email: player.email || '',
          password: player.password || '',
          created_at: player.created_at || '',
          last_login: player.last_login || '',
          stats: player.stats || {
            total_games: 0,
            total_score: 0,
            best_score: 0,
            favorite_mode: '',
            favorite_category: ''
          },
          score: player.score || 0,
          mode: player.mode || '',
          categoria: player.categoria || '',
          correctas: player.correctas || 0,
          incorrectas: player.incorrectas || 0,
          tiempo: player.tiempo || 0,
          fecha: player.fecha || '',
          is_admin: player.is_admin || false
        }));
        
        console.log('Jugadores formateados:', formattedPlayers);
        setPlayers(formattedPlayers);
      } else {
        console.error('Error en la respuesta:', response.status, response.statusText);
        setError('Error al cargar los jugadores');
      }
    } catch (error) {
      console.error('Error de conexión:', error);
      setError('Error de conexión: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const sortPlayers = () => {
    setPlayers([...players].sort((a, b) => b.score - a.score));
  };

  const deletePlayer = async (id) => {
    if (!window.confirm('¿Eliminar este jugador?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/players/${id}`, { method: 'DELETE' });
      if (response.ok) {
        setPlayers(players.filter(player => player.id !== id));
      } else {
        alert('Error al eliminar jugador');
      }
    } catch (error) {
      alert('Error de conexión: ' + error.message);
    }
  };

  const openEditModal = (player) => {
    setCurrentPlayer({ ...player });
    setIsModalOpen(true);
  };

  const savePlayerChanges = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/players/${currentPlayer.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentPlayer)
      });
      if (response.ok) {
        setPlayers(players.map(p => p.id === currentPlayer.id ? currentPlayer : p));
        setIsModalOpen(false);
        setCurrentPlayer(null);
      } else {
        alert('Error al actualizar jugador');
      }
    } catch (error) {
      alert('Error de conexión: ' + error.message);
    }
  };

  const handleModalPlayerChange = (e) => {
    const { name, value } = e.target;
    
    // Manejar campos anidados como stats
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setCurrentPlayer({
        ...currentPlayer,
        [parent]: {
          ...currentPlayer[parent],
          [child]: value
        }
      });
    } else {
      setCurrentPlayer({ ...currentPlayer, [name]: value });
    }
  };

  const handleSaveAllChanges = () => {
    alert('¡Cambios en jugadores guardados!');
  };

  const handleNewPlayerChange = (e) => {
    setNewPlayer({ ...newPlayer, [e.target.name]: e.target.value });
  };

  const addPlayer = async () => {
    if (!newPlayer.username.trim()) return;
    try {
      const response = await fetch(`${API_BASE_URL}/players`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPlayer)
      });
      if (response.ok) {
        const data = await response.json();
        setPlayers([...players, data.player]);
        setNewPlayer({ username: '', score: 0, mode: '', categoria: '', correctas: 0, incorrectas: 0, tiempo: 0 });
      } else {
        alert('Error al agregar jugador');
      }
    } catch (error) {
      alert('Error de conexión: ' + error.message);
    }
  };

  if (loading) {
    return <div className="p-6 bg-white rounded-xl shadow-lg m-6">Cargando jugadores...</div>;
  }
  if (error) {
    return <div className="p-6 bg-white rounded-xl shadow-lg m-6 text-red-600">{error}</div>;
  }

  return (
    <div className="p-6 bg-white rounded-xl shadow-lg m-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Gestión de Jugadores</h2>
      <button
        onClick={sortPlayers}
        className="mb-6 px-6 py-2 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 transition-colors"
      >
        Ordenar por Puntaje
      </button>
      <div className="mb-6 flex gap-4">
        <input type="text" name="username" placeholder="Nombre" value={newPlayer.username} onChange={handleNewPlayerChange} className="p-3 border border-gray-300 rounded-lg flex-1" />
        <input type="number" name="score" placeholder="Puntaje" value={newPlayer.score} onChange={handleNewPlayerChange} className="p-3 border border-gray-300 rounded-lg flex-1" />
        <input type="text" name="mode" placeholder="Modo" value={newPlayer.mode} onChange={handleNewPlayerChange} className="p-3 border border-gray-300 rounded-lg flex-1" />
        <input type="text" name="categoria" placeholder="Categoría" value={newPlayer.categoria} onChange={handleNewPlayerChange} className="p-3 border border-gray-300 rounded-lg flex-1" />
        <button onClick={addPlayer} className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700">Agregar</button>
      </div>
      <div className="overflow-y-auto" style={{maxHeight: '500px', overflowX: 'hidden'}}>
        <table className="w-full bg-white rounded-xl shadow-sm" style={{tableLayout: 'fixed'}}>
          <thead className="sticky top-0 bg-gray-100">
            <tr className="border-b border-gray-200 text-gray-600 uppercase text-xs leading-tight">
              <th className="py-1 px-1 text-left" style={{maxWidth: '40px'}}>ID</th>
              <th className="py-1 px-1 text-left" style={{maxWidth: '80px'}}>Usuario</th>
              <th className="py-1 px-1 text-left" style={{maxWidth: '100px'}}>Nombre</th>
              <th className="py-1 px-1 text-left" style={{maxWidth: '60px'}}>Email</th>
              <th className="py-1 px-1 text-left" style={{maxWidth: '50px'}}>Juegos</th>
              <th className="py-1 px-1 text-left" style={{maxWidth: '60px'}}>Mejor Puntaje</th>
              <th className="py-1 px-1 text-left" style={{maxWidth: '80px'}}>Último Login</th>
              <th className="py-1 px-1 text-center" style={{maxWidth: '80px'}}>Acciones</th>
            </tr>
          </thead>
          <tbody className="text-gray-700 text-xs font-light">
            {players.filter(player => !player.is_admin).map((player) => (
              <tr key={player.id} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="py-0.5 px-1 text-left whitespace-nowrap overflow-hidden text-ellipsis" style={{maxWidth: '40px'}}>{player.id}</td>
                <td className="py-0.5 px-1 text-left overflow-hidden text-ellipsis whitespace-nowrap" style={{maxWidth: '80px'}}>{player.username}</td>
                <td className="py-0.5 px-1 text-left overflow-hidden text-ellipsis whitespace-nowrap" style={{maxWidth: '100px'}}>{player.fullName}</td>
                <td className="py-0.5 px-1 text-left overflow-hidden text-ellipsis whitespace-nowrap" style={{maxWidth: '60px'}}>{player.email || '-'}</td>
                <td className="py-0.5 px-1 text-left" style={{maxWidth: '50px'}}>{player.stats?.total_games || 0}</td>
                <td className="py-0.5 px-1 text-left" style={{maxWidth: '60px'}}>{player.stats?.best_score || 0}</td>
                <td className="py-0.5 px-1 text-left overflow-hidden text-ellipsis whitespace-nowrap" style={{maxWidth: '80px'}}>
                  {player.last_login ? new Date(player.last_login).toLocaleDateString() : '-'}
                </td>
                <td className="py-0.5 px-1 text-center whitespace-nowrap" style={{maxWidth: '80px'}}>
                  <button onClick={() => openEditModal(player)} className="bg-blue-500 text-white py-0.5 px-1 rounded-md hover:bg-blue-600 transition-colors mr-1 text-xs">Editar</button>
                  <button onClick={() => deletePlayer(player.id)} className="bg-red-500 text-white py-0.5 px-1 rounded-md hover:bg-red-600 transition-colors text-xs">Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {isModalOpen && currentPlayer && (
        <Modal onClose={() => setIsModalOpen(false)}>
          <div style={{maxHeight: '80vh', overflowY: 'auto', paddingRight: '8px'}}>
            <h3 className="text-xl font-bold mb-4">Editar Jugador</h3>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">Nombre de usuario:</label>
              <input type="text" name="username" value={currentPlayer.username} onChange={handleModalPlayerChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">Nombre completo:</label>
              <input type="text" name="fullName" value={currentPlayer.fullName || ''} onChange={handleModalPlayerChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">Email:</label>
              <input type="email" name="email" value={currentPlayer.email || ''} onChange={handleModalPlayerChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">Contraseña actual (hash):</label>
              <input type="text" name="password" value={currentPlayer.password || ''} disabled className="w-full p-3 border border-gray-200 rounded-lg bg-gray-100" />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">Nueva contraseña (dejar vacío para no cambiar):</label>
              <input type="password" name="newPassword" value={currentPlayer.newPassword || ''} onChange={e => setCurrentPlayer({ ...currentPlayer, newPassword: e.target.value })} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" autoComplete="new-password" />
            </div>
            <div className="mb-4 grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Fecha de creación:</label>
                <input type="text" name="created_at" value={currentPlayer.created_at || ''} disabled className="w-full p-3 border border-gray-200 rounded-lg bg-gray-100" />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Último login:</label>
                <input type="text" name="last_login" value={currentPlayer.last_login || ''} disabled className="w-full p-3 border border-gray-200 rounded-lg bg-gray-100" />
              </div>
            </div>
            <h4 className="text-lg font-semibold mt-6 mb-2 text-blue-700">Estadísticas</h4>
            <div className="mb-4 grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Total de juegos:</label>
                <input type="number" name="stats.total_games" value={currentPlayer.stats?.total_games || 0} disabled className="w-full p-3 border border-gray-200 rounded-lg bg-gray-100" />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Puntaje total:</label>
                <input type="number" name="stats.total_score" value={currentPlayer.stats?.total_score || 0} disabled className="w-full p-3 border border-gray-200 rounded-lg bg-gray-100" />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Mejor puntaje:</label>
                <input type="number" name="stats.best_score" value={currentPlayer.stats?.best_score || 0} disabled className="w-full p-3 border border-gray-200 rounded-lg bg-gray-100" />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Modo favorito:</label>
                <input type="text" name="stats.favorite_mode" value={currentPlayer.stats?.favorite_mode || ''} disabled className="w-full p-3 border border-gray-200 rounded-lg bg-gray-100" />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Categoría favorita:</label>
                <input type="text" name="stats.favorite_category" value={currentPlayer.stats?.favorite_category || ''} disabled className="w-full p-3 border border-gray-200 rounded-lg bg-gray-100" />
              </div>
            </div>
            <h4 className="text-lg font-semibold mt-6 mb-2 text-blue-700">Datos de la última partida</h4>
            <div className="mb-4 grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Puntaje:</label>
                <input type="number" name="score" value={currentPlayer.score} onChange={handleModalPlayerChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Modo:</label>
                <input type="text" name="mode" value={currentPlayer.mode} onChange={handleModalPlayerChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Categoría:</label>
                <input type="text" name="categoria" value={currentPlayer.categoria} onChange={handleModalPlayerChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Correctas:</label>
                <input type="number" name="correctas" value={currentPlayer.correctas} onChange={handleModalPlayerChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Incorrectas:</label>
                <input type="number" name="incorrectas" value={currentPlayer.incorrectas} onChange={handleModalPlayerChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Tiempo:</label>
                <input type="number" name="tiempo" value={currentPlayer.tiempo} onChange={handleModalPlayerChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
            <button onClick={savePlayerChanges} className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 mr-2">Guardar</button>
            <button onClick={() => setIsModalOpen(false)} className="bg-gray-400 text-white px-6 py-2 rounded-lg hover:bg-gray-500">Cancelar</button>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default PlayersManagement;