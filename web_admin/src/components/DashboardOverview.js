import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';

const API_BASE_URL = 'http://localhost:5000/api';
const SOCKET_URL = 'http://localhost:5000';

const DashboardOverview = () => {
  const [stats, setStats] = useState({
    total_questions: 0,
    total_players: 0,
    total_games: 0,
    questions_by_category: {},
    questions_by_difficulty: {},
    top_players: []
  });
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStats();
    fetchCategories();
    // Conexión WebSocket para actualización en tiempo real
    const socket = io(SOCKET_URL);
    socket.on('data_update', (data) => {
      if (data && (data.type === 'ranking' || data.type === 'players')) {
        loadStats();
      }
      if (data && data.type === 'categories') {
        fetchCategories();
      }
    });
    return () => {
      socket.disconnect();
    };
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        setError('Error al cargar las estadísticas');
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/categories`);
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      }
    } catch (e) {
      // No hacer nada, solo evitar crash
    }
  };

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-xl shadow-lg m-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-gray-600">Cargando estadísticas...</div>
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
            onClick={loadStats}
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
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Panel de Control</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-blue-100 p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">Total de Preguntas</h3>
          <p className="text-3xl font-bold text-blue-600">{stats.total_questions}</p>
        </div>
        
        <div className="bg-green-100 p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-green-800 mb-2">Jugadores Registrados</h3>
          <p className="text-3xl font-bold text-green-600">{stats.total_players}</p>
          <p className="text-sm text-green-700 mt-1">Usuarios únicos en el sistema</p>
        </div>
        
        <div className="bg-purple-100 p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-purple-800 mb-2">Partidas Jugadas</h3>
          <p className="text-3xl font-bold text-purple-600">{stats.total_games}</p>
        </div>
        
        <div className="bg-orange-100 p-6 rounded-xl">
          <h3 className="text-lg font-semibold text-orange-800 mb-2">Jugadores Activos</h3>
          <p className="text-3xl font-bold text-orange-600">{stats.total_games > 0 ? Math.min(stats.total_players, stats.total_games) : 0}</p>
          <p className="text-sm text-orange-700 mt-1">Con al menos una partida</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-50 p-6 rounded-xl">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">Preguntas por Categoría</h3>
          <div className="space-y-2">
            {categories.map(category => (
              <div key={category} className="flex justify-between items-center">
                <span className="text-gray-700">{category}</span>
                <span className="font-semibold text-blue-600">{stats.questions_by_category[category] || 0}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-gray-50 p-6 rounded-xl">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">Preguntas por Dificultad</h3>
          <div className="space-y-2">
            {Object.entries(stats.questions_by_difficulty).map(([difficulty, count]) => (
              <div key={difficulty} className="flex justify-between items-center">
                <span className="text-gray-700">{difficulty}</span>
                <span className="font-semibold text-green-600">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>


    </div>
  );
};

export default DashboardOverview;