import React, { useState, useEffect } from 'react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

const PlayerStats = () => {
  const [userStats, setUserStats] = useState({});
  const [achievements, setAchievements] = useState([]);
  const [gameHistory, setGameHistory] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, achievementsRes, historyRes] = await Promise.all([
        fetch('http://localhost:5000/api/user_stats'),
        fetch('http://localhost:5000/api/achievements'),
        fetch('http://localhost:5000/api/game_history')
      ]);

      const statsData = await statsRes.json();
      const achievementsData = await achievementsRes.json();
      const historyData = await historyRes.json();

      setUserStats(statsData.users || {});
      setAchievements(achievementsData);
      setGameHistory(historyData.history || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  const getSelectedUserStats = () => {
    return userStats[selectedUser] || {};
  };

  const getSelectedUserHistory = () => {
    return gameHistory.filter(game => game.username === selectedUser);
  };

  const getModeDistributionData = () => {
    const stats = getSelectedUserStats();
    return {
      labels: ['Clásico', 'Contrareloj', 'Duelo'],
      datasets: [{
        label: 'Partidas',
        data: [
          stats.classic_games || 0,
          stats.timeattack_games || 0,
          stats.duel_games || 0
        ],
        backgroundColor: ['#2ecc71', '#3498db', '#e74c3c'],
        borderColor: ['#27ae60', '#2980b9', '#c0392b'],
        borderWidth: 2
      }]
    };
  };

  const getAccuracyData = () => {
    const stats = getSelectedUserStats();
    const totalCorrect = stats.total_correct || 0;
    const totalIncorrect = stats.total_incorrect || 0;
    const total = totalCorrect + totalIncorrect;

    if (total === 0) return null;

    const accuracy = (totalCorrect / total) * 100;
    const errorRate = 100 - accuracy;

    return {
      labels: ['Correctas', 'Incorrectas'],
      datasets: [{
        data: [accuracy, errorRate],
        backgroundColor: ['#2ecc71', '#e74c3c'],
        borderColor: ['#27ae60', '#c0392b'],
        borderWidth: 2
      }]
    };
  };

  const getPerformanceOverTime = () => {
    const userHistory = getSelectedUserHistory();
    const sortedHistory = userHistory
      .sort((a, b) => new Date(a.fecha) - new Date(b.fecha))
      .slice(-10); // Últimas 10 partidas

    return {
      labels: sortedHistory.map(game => new Date(game.fecha).toLocaleDateString()),
      datasets: [{
        label: 'Puntuación',
        data: sortedHistory.map(game => game.puntuacion),
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        tension: 0.4
      }]
    };
  };

  const getAchievementsProgress = () => {
    const stats = getSelectedUserStats();
    const unlockedCount = achievements.filter(achievement => 
      stats.unlocked_achievements && stats.unlocked_achievements.includes(achievement.id)
    ).length;
    const totalCount = achievements.length;

    return {
      labels: ['Desbloqueados', 'Pendientes'],
      datasets: [{
        data: [unlockedCount, totalCount - unlockedCount],
        backgroundColor: ['#f1c40f', '#95a5a6'],
        borderColor: ['#f39c12', '#7f8c8d'],
        borderWidth: 2
      }]
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">📊 Estadísticas Detalladas</h1>

        {/* Selector de Usuario */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Seleccionar Usuario:
          </label>
          <select
            value={selectedUser}
            onChange={(e) => setSelectedUser(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Selecciona un usuario</option>
            {Object.keys(userStats).map(username => (
              <option key={username} value={username}>{username}</option>
            ))}
          </select>
        </div>

        {selectedUser && (
          <>
            {/* Resumen General */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                📈 Resumen de {selectedUser}
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {getSelectedUserStats().total_games || 0}
                  </div>
                  <div className="text-sm text-gray-600">Total de Juegos</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {getSelectedUserStats().total_correct || 0}
                  </div>
                  <div className="text-sm text-gray-600">Respuestas Correctas</div>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {getSelectedUserStats().total_incorrect || 0}
                  </div>
                  <div className="text-sm text-gray-600">Respuestas Incorrectas</div>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">
                    {getSelectedUserStats().highest_score || 0}
                  </div>
                  <div className="text-sm text-gray-600">Puntuación Más Alta</div>
                </div>
              </div>
            </div>

            {/* Gráficos */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Distribución por Modos */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  🎮 Distribución por Modos
                </h3>
                <Bar
                  data={getModeDistributionData()}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: { display: false },
                      title: { display: false }
                    }
                  }}
                />
              </div>

              {/* Precisión */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  🎯 Precisión del Jugador
                </h3>
                {getAccuracyData() ? (
                  <Doughnut
                    data={getAccuracyData()}
                    options={{
                      responsive: true,
                      plugins: {
                        legend: { position: 'bottom' },
                        title: { display: false }
                      }
                    }}
                  />
                ) : (
                  <div className="text-center text-gray-500 py-8">
                    Sin datos suficientes para mostrar precisión
                  </div>
                )}
              </div>
            </div>

            {/* Rendimiento en el Tiempo */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                📈 Rendimiento en el Tiempo
              </h3>
              <Line
                data={getPerformanceOverTime()}
                options={{
                  responsive: true,
                  plugins: {
                    legend: { display: false },
                    title: { display: false }
                  },
                  scales: {
                    y: {
                      beginAtZero: true
                    }
                  }
                }}
              />
            </div>

            {/* Progreso de Logros */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                🏆 Progreso de Logros
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <Doughnut
                    data={getAchievementsProgress()}
                    options={{
                      responsive: true,
                      plugins: {
                        legend: { position: 'bottom' },
                        title: { display: false }
                      }
                    }}
                  />
                </div>
                <div className="space-y-4">
                  <h4 className="font-semibold text-gray-900">Logros Desbloqueados:</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {achievements.map(achievement => {
                      const isUnlocked = getSelectedUserStats().unlocked_achievements?.includes(achievement.id);
                      return (
                        <div
                          key={achievement.id}
                          className={`p-3 rounded-lg border ${
                            isUnlocked 
                              ? 'bg-green-50 border-green-200' 
                              : 'bg-gray-50 border-gray-200'
                          }`}
                        >
                          <div className="flex items-center space-x-2">
                            <span className="text-lg">{achievement.icon}</span>
                            <div>
                              <div className={`font-medium ${
                                isUnlocked ? 'text-green-800' : 'text-gray-600'
                              }`}>
                                {achievement.name}
                              </div>
                              <div className="text-xs text-gray-500">
                                {achievement.description}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>

            {/* Historial de Partidas */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                📋 Historial de Partidas Recientes
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Fecha
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Modo
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Categoría
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Puntuación
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Aciertos
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Errores
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {getSelectedUserHistory()
                      .sort((a, b) => new Date(b.fecha) - new Date(a.fecha))
                      .slice(0, 10)
                      .map((game, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(game.fecha).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {game.modo}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {game.categoria}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                            {game.puntuacion}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                            {game.correctas}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                            {game.incorrectas}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default PlayerStats; 