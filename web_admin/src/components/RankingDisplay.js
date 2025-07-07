import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:5000/api';

const RankingDisplay = () => {
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMode, setSelectedMode] = useState('Todos');
  const [selectedCategory, setSelectedCategory] = useState('Todas');
  const [viewMode, setViewMode] = useState('all'); // 'all', 'unique', 'byMode'
  const [availableModes, setAvailableModes] = useState([]);
  const [availableCategories, setAvailableCategories] = useState([]);

  useEffect(() => {
    loadRanking();
    loadGameData();
  }, []);

  const loadRanking = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/ranking`);
      if (response.ok) {
        const data = await response.json();
        // Aceptar tanto lista como objeto con 'rankings'
        if (Array.isArray(data)) {
          setRanking(data);
        } else if (data && Array.isArray(data.rankings)) {
          setRanking(data.rankings);
        } else {
          setRanking([]);
        }
      } else {
        setError('Error al cargar el ranking');
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const loadGameData = async () => {
    try {
      // Cargar modos de juego
      const modesResponse = await fetch(`${API_BASE_URL}/game-modes`);
      if (modesResponse.ok) {
        const modesData = await modesResponse.json();
        setAvailableModes(modesData.map(mode => mode.name));
      }

      // Cargar categorías
      const categoriesResponse = await fetch(`${API_BASE_URL}/categories`);
      if (categoriesResponse.ok) {
        const categoriesData = await categoriesResponse.json();
        setAvailableCategories(categoriesData);
      }
    } catch (error) {
      console.log('Error cargando datos del juego:', error);
      // Fallback a datos por defecto si no se pueden cargar
      setAvailableModes(['Clásico', 'Contrarreloj', 'Duelo']);
      setAvailableCategories(['Ciencia', 'Historia', 'Arte', 'Deportes', 'Entretenimiento', 'Geografía']);
    }
  };

  // Obtener modos únicos (incluyendo los disponibles y los jugados)
  const getUniqueModes = () => {
    const playedModes = [...new Set(ranking.map(player => player.mode))];
    const allModes = [...new Set([...availableModes, ...playedModes])];
    return ['Todos', ...allModes];
  };

  // Obtener categorías únicas (incluyendo las disponibles y las jugadas)
  const getUniqueCategories = () => {
    const playedCategories = [...new Set(ranking.map(player => player.categoria).filter(cat => cat))];
    const allCategories = [...new Set([...availableCategories, ...playedCategories])];
    return ['Todas', ...allCategories];
  };

  // Filtrar datos según selección y solo jugadores
  const getFilteredData = () => {
    let filtered = ranking.filter(player => !player.is_admin);
    
    if (selectedMode !== 'Todos') {
      filtered = filtered.filter(player => player.mode === selectedMode);
    }
    
    if (selectedCategory !== 'Todas') {
      filtered = filtered.filter(player => player.categoria === selectedCategory);
    }
    
    return filtered;
  };

  // Vista de jugadores únicos (mejor puntaje por jugador)
  const getUniquePlayersRanking = () => {
    const uniquePlayers = {};
    const filteredData = getFilteredData();
    
    filteredData.forEach(player => {
      const key = `${player.username}-${player.mode}-${player.categoria}`;
      if (!uniquePlayers[key] || player.score > uniquePlayers[key].score) {
        uniquePlayers[key] = player;
      }
    });
    
    return Object.values(uniquePlayers).sort((a, b) => b.score - a.score);
  };

  // Vista agrupada por modo
  const getRankingByMode = () => {
    const filteredData = getFilteredData();
    const grouped = {};
    
    // Inicializar todos los modos disponibles
    availableModes.forEach(mode => {
      grouped[mode] = [];
    });
    
    filteredData.forEach(player => {
      const mode = player.mode || 'Sin modo';
      if (!grouped[mode]) {
        grouped[mode] = [];
      }
      grouped[mode].push(player);
    });
    
    // Ordenar cada grupo por puntuación
    Object.keys(grouped).forEach(mode => {
      grouped[mode].sort((a, b) => b.score - a.score);
    });
    
    return grouped;
  };

  const filteredData = getFilteredData();
  const uniqueRanking = getUniquePlayersRanking();
  const rankingByMode = getRankingByMode();
  const modes = getUniqueModes();
  const categories = getUniqueCategories();

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-xl shadow-lg m-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-gray-600">Cargando ranking...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-white rounded-xl shadow-lg m-6">
        <div className="text-red-600 text-center">
          <h3 className="text-xl font-bold mb-2">Error</h3>
          <p>{error}</p>
          <button 
            onClick={loadRanking}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-xl shadow-lg m-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Ranking de Jugadores</h2>
        <button 
          onClick={loadRanking}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          🔄 Actualizar
        </button>
      </div>

      {/* Filtros */}
      <div className="mb-6 flex flex-wrap gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Modo:</label>
          <select 
            value={selectedMode} 
            onChange={(e) => setSelectedMode(e.target.value)}
            className="border border-gray-300 rounded px-3 py-2"
          >
            {modes.map(mode => (
              <option key={mode} value={mode}>
                {mode} {ranking.filter(p => p.mode === mode).length > 0 ? `(${ranking.filter(p => p.mode === mode).length})` : '(Sin datos)'}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Categoría:</label>
          <select 
            value={selectedCategory} 
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="border border-gray-300 rounded px-3 py-2"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category} {ranking.filter(p => p.categoria === category).length > 0 ? `(${ranking.filter(p => p.categoria === category).length})` : '(Sin datos)'}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Vista:</label>
          <select 
            value={viewMode} 
            onChange={(e) => setViewMode(e.target.value)}
            className="border border-gray-300 rounded px-3 py-2"
          >
            <option value="all">Todas las puntuaciones</option>
            <option value="unique">Mejor por jugador</option>
            <option value="byMode">Agrupado por modo</option>
          </select>
        </div>
      </div>

      {/* Estadísticas */}
      <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{filteredData.length}</div>
          <div className="text-sm text-gray-600">Total puntuaciones</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{uniqueRanking.length}</div>
          <div className="text-sm text-gray-600">Jugadores únicos</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">{availableModes.length}</div>
          <div className="text-sm text-gray-600">Modos disponibles</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-orange-600">{availableCategories.length}</div>
          <div className="text-sm text-gray-600">Categorías disponibles</div>
        </div>
      </div>

      {/* Vista de todas las puntuaciones */}
      {viewMode === 'all' && (
        <div>
          <h3 className="text-lg font-semibold mb-4 text-gray-700">Todas las Puntuaciones</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white rounded-xl shadow-sm">
              <thead>
                <tr className="bg-gray-100 border-b border-gray-200 text-gray-600 uppercase text-sm leading-normal">
                  <th className="py-3 px-6 text-left">Posición</th>
                  <th className="py-3 px-6 text-left">Nombre</th>
                  <th className="py-3 px-6 text-left">Puntaje</th>
                  <th className="py-3 px-6 text-left">Modo</th>
                  <th className="py-3 px-6 text-left">Categoría</th>
                  <th className="py-3 px-6 text-left">Correctas</th>
                  <th className="py-3 px-6 text-left">Incorrectas</th>
                  <th className="py-3 px-6 text-left">Tiempo</th>
                  <th className="py-3 px-6 text-left">Fecha</th>
                </tr>
              </thead>
              <tbody className="text-gray-700 text-sm font-light">
                {filteredData.map((player, index) => (
                  <tr key={`${player.id}-${index}`} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="py-3 px-6 text-left whitespace-nowrap font-semibold">{index + 1}</td>
                    <td className="py-3 px-6 text-left font-medium">{player.username}</td>
                    <td className="py-3 px-6 text-left font-bold text-blue-600">{player.score}</td>
                    <td className="py-3 px-6 text-left">{player.mode}</td>
                    <td className="py-3 px-6 text-left">{player.categoria || 'N/A'}</td>
                    <td className="py-3 px-6 text-left text-green-600">{player.correctas || 0}</td>
                    <td className="py-3 px-6 text-left text-red-600">{player.incorrectas || 0}</td>
                    <td className="py-3 px-6 text-left">{player.tiempo || 0}s</td>
                    <td className="py-3 px-6 text-left">
                      {player.fecha ? new Date(player.fecha).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Vista de mejores puntuaciones por jugador */}
      {viewMode === 'unique' && (
        <div>
          <h3 className="text-lg font-semibold mb-4 text-gray-700">Mejores Puntuaciones por Jugador</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded-xl shadow-sm">
          <thead>
            <tr className="bg-gray-100 border-b border-gray-200 text-gray-600 uppercase text-sm leading-normal">
              <th className="py-3 px-6 text-left">Posición</th>
              <th className="py-3 px-6 text-left">Nombre</th>
              <th className="py-3 px-6 text-left">Puntaje</th>
              <th className="py-3 px-6 text-left">Modo</th>
              <th className="py-3 px-6 text-left">Categoría</th>
              <th className="py-3 px-6 text-left">Correctas</th>
              <th className="py-3 px-6 text-left">Fecha</th>
            </tr>
          </thead>
          <tbody className="text-gray-700 text-sm font-light">
            {uniqueRanking.map((player, index) => (
              <tr key={player.id} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="py-3 px-6 text-left whitespace-nowrap font-semibold">{index + 1}</td>
                    <td className="py-3 px-6 text-left font-medium">{player.username}</td>
                    <td className="py-3 px-6 text-left font-bold text-blue-600">{player.score}</td>
                <td className="py-3 px-6 text-left">{player.mode}</td>
                <td className="py-3 px-6 text-left">{player.categoria || 'N/A'}</td>
                    <td className="py-3 px-6 text-left text-green-600">{player.correctas || 0}</td>
                    <td className="py-3 px-6 text-left">
                      {player.fecha ? new Date(player.fecha).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Vista agrupada por modo */}
      {viewMode === 'byMode' && (
        <div>
          <h3 className="text-lg font-semibold mb-4 text-gray-700">Ranking por Modo de Juego</h3>
          {Object.entries(rankingByMode).map(([mode, players]) => (
            <div key={mode} className="mb-8">
              <h4 className="text-md font-semibold mb-3 text-gray-600 bg-gray-50 p-3 rounded">
                🎮 {mode} ({players.length} puntuaciones)
                {players.length === 0 && <span className="text-gray-400 ml-2">- Sin datos aún</span>}
              </h4>
              {players.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full bg-white rounded-xl shadow-sm">
                    <thead>
                      <tr className="bg-gray-100 border-b border-gray-200 text-gray-600 uppercase text-sm leading-normal">
                        <th className="py-3 px-6 text-left">Posición</th>
                        <th className="py-3 px-6 text-left">Nombre</th>
                        <th className="py-3 px-6 text-left">Puntaje</th>
                        <th className="py-3 px-6 text-left">Categoría</th>
                        <th className="py-3 px-6 text-left">Correctas</th>
                        <th className="py-3 px-6 text-left">Fecha</th>
                      </tr>
                    </thead>
                    <tbody className="text-gray-700 text-sm font-light">
                      {players.map((player, index) => (
                        <tr key={`${mode}-${player.id}`} className="border-b border-gray-200 hover:bg-gray-50">
                          <td className="py-3 px-6 text-left whitespace-nowrap font-semibold">{index + 1}</td>
                          <td className="py-3 px-6 text-left font-medium">{player.username}</td>
                          <td className="py-3 px-6 text-left font-bold text-blue-600">{player.score}</td>
                          <td className="py-3 px-6 text-left">{player.categoria || 'N/A'}</td>
                          <td className="py-3 px-6 text-left text-green-600">{player.correctas || 0}</td>
                <td className="py-3 px-6 text-left">
                  {player.fecha ? new Date(player.fecha).toLocaleDateString() : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
              ) : (
                <div className="text-center py-4 text-gray-500 bg-gray-50 rounded">
                  <p>No hay puntuaciones registradas para este modo aún.</p>
                  <p className="text-sm">¡Sé el primero en jugar {mode}!</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {filteredData.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No hay puntuaciones registradas con los filtros seleccionados.</p>
          {selectedMode !== 'Todos' && selectedCategory !== 'Todas' && (
            <p className="text-sm mt-2">¡Sé el primero en jugar {selectedMode} en {selectedCategory}!</p>
          )}
        </div>
      )}
    </div>
  );
};

export default RankingDisplay;