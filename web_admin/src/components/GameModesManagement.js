import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

const GameModesManagement = () => {
  const [gameModes, setGameModes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingMode, setEditingMode] = useState(null);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Conectar WebSocket
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);

    // Escuchar actualizaciones
    newSocket.on('data_update', (data) => {
      if (data.type === 'game_modes') {
        loadGameModes();
      }
    });

    loadGameModes();

    return () => {
      if (newSocket) newSocket.close();
    };
  }, []);

  const loadGameModes = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/game-modes');
      if (response.ok) {
        const data = await response.json();
        setGameModes(data);
        setError(null);
      } else {
        setError('Error cargando modos de juego');
      }
    } catch (err) {
      setError('Error de conexión');
    } finally {
      setLoading(false);
    }
  };

  const saveGameModes = async (updatedModes) => {
    try {
      const response = await fetch('http://localhost:5000/api/game-modes', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedModes),
      });

      if (response.ok) {
        const result = await response.json();
        setGameModes(result.game_modes);
        setEditingMode(null);
        
        // Notificar actualización vía WebSocket
        if (socket) {
          socket.emit('data_update', { type: 'game_modes' });
        }
        
        return true;
      } else {
        setError('Error guardando modos de juego');
        return false;
      }
    } catch (err) {
      setError('Error de conexión');
      return false;
    }
  };

  const handleEditMode = (modeIndex) => {
    setEditingMode(modeIndex);
  };

  const handleSaveMode = async (modeIndex) => {
    const updatedModes = [...gameModes];
    const success = await saveGameModes(updatedModes);
    if (success) {
      setEditingMode(null);
    }
  };

  const handleCancelEdit = () => {
    setEditingMode(null);
    loadGameModes(); // Recargar datos originales
  };

  const handleInputChange = (modeIndex, field, value) => {
    const updatedModes = [...gameModes];
    updatedModes[modeIndex] = {
      ...updatedModes[modeIndex],
      [field]: value
    };
    setGameModes(updatedModes);
  };

  const getModeDescription = (mode) => {
    if (mode.isGlobalTimer) {
      return `${mode.totalTime} segundos en total\nPreguntas ilimitadas\nPuntos extras por velocidad`;
    } else {
      return `${mode.timePerQuestion} segundos por pregunta\n${mode.numQuestions} preguntas\nDificultad progresiva`;
    }
  };

  const getModeIcon = (modeName) => {
    const icons = {
      'Clásico': '🎮',
      'Contrarreloj': '⏱️',
      'Duelo': '⚔️'
    };
    return icons[modeName] || '🎯';
  };

  const getModeColor = (modeName) => {
    const colors = {
      'Clásico': '#2ecc71',
      'Contrarreloj': '#3498db',
      'Duelo': '#e74c3c'
    };
    return colors[modeName] || '#95a5a6';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        <strong>Error:</strong> {error}
        <button 
          onClick={loadGameModes}
          className="ml-4 bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
        >
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Gestión de Modos de Juego</h2>
        <button
          onClick={loadGameModes}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
        >
          🔄 Actualizar
        </button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {gameModes
          .filter(mode => ['Clásico', 'Contrarreloj', 'Duelo'].includes(mode.name))
          .map((mode, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden"
            >
              {/* Header del modo */}
              <div 
                className="p-4 text-white"
                style={{ backgroundColor: getModeColor(mode.name) }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">{getModeIcon(mode.name)}</span>
                    <h3 className="text-lg font-semibold">{mode.name}</h3>
                  </div>
                  {editingMode === index ? (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleSaveMode(index)}
                        className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                      >
                        ✅ Guardar
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        className="bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600"
                      >
                        ❌ Cancelar
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleEditMode(index)}
                      className="bg-white bg-opacity-20 text-white px-3 py-1 rounded text-sm hover:bg-opacity-30"
                    >
                      ✏️ Editar
                    </button>
                  )}
                </div>
              </div>

              {/* Contenido del modo */}
              <div className="p-4">
                {editingMode === index ? (
                  <div className="space-y-4">
                    {/* Nombre del modo */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Nombre del Modo
                      </label>
                      <input
                        type="text"
                        value={mode.name}
                        onChange={(e) => handleInputChange(index, 'name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    {/* Tipo de temporizador */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Tipo de Temporizador
                      </label>
                      <select
                        value={mode.isGlobalTimer ? 'global' : 'per_question'}
                        onChange={(e) => {
                          const isGlobal = e.target.value === 'global';
                          handleInputChange(index, 'isGlobalTimer', isGlobal);
                          if (isGlobal) {
                            handleInputChange(index, 'totalTime', mode.totalTime || 60);
                          } else {
                            handleInputChange(index, 'timePerQuestion', mode.timePerQuestion || 30);
                            handleInputChange(index, 'numQuestions', mode.numQuestions || 15);
                          }
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="per_question">Por pregunta</option>
                        <option value="global">Tiempo global</option>
                      </select>
                    </div>

                    {/* Configuración específica según el tipo */}
                    {mode.isGlobalTimer ? (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Tiempo Total (segundos)
                        </label>
                        <input
                          type="number"
                          min="10"
                          max="600"
                          value={mode.totalTime || 60}
                          onChange={(e) => handleInputChange(index, 'totalTime', parseInt(e.target.value))}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    ) : (
                      <>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Tiempo por Pregunta (segundos)
                          </label>
                          <input
                            type="number"
                            min="5"
                            max="120"
                            value={mode.timePerQuestion || 30}
                            onChange={(e) => handleInputChange(index, 'timePerQuestion', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Número de Preguntas
                          </label>
                          <input
                            type="number"
                            min="1"
                            max="50"
                            value={mode.numQuestions || 15}
                            onChange={(e) => handleInputChange(index, 'numQuestions', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </>
                    )}

                    {/* Configuración de puntuación para todos los modos */}
                    <div className="border-t pt-4">
                      <h4 className="font-medium text-gray-800 mb-3">🎯 Configuración de Puntuación</h4>
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Puntos por Respuesta Correcta
                          </label>
                          <input
                            type="number"
                            min="10"
                            max="1000"
                            value={mode.points_correct || 100}
                            onChange={(e) => handleInputChange(index, 'points_correct', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Puntos por Respuesta Incorrecta
                          </label>
                          <input
                            type="number"
                            min="-1000"
                            max="0"
                            value={mode.points_incorrect || -25}
                            onChange={(e) => handleInputChange(index, 'points_incorrect', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Bonificación por Racha
                          </label>
                          <input
                            type="number"
                            min="0"
                            max="500"
                            value={mode.bonus_streak || 50}
                            onChange={(e) => handleInputChange(index, 'bonus_streak', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Umbral de Racha (aciertos)
                          </label>
                          <input
                            type="number"
                            min="2"
                            max="10"
                            value={mode.bonus_streak_threshold || 3}
                            onChange={(e) => handleInputChange(index, 'bonus_streak_threshold', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Bonificación por Puntuación Perfecta
                          </label>
                          <input
                            type="number"
                            min="0"
                            max="1000"
                            value={mode.bonus_perfect || 0}
                            onChange={(e) => handleInputChange(index, 'bonus_perfect', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Bonificación por Velocidad (por segundo)
                          </label>
                          <input
                            type="number"
                            min="0"
                            max="100"
                            value={mode.bonus_speed || 0}
                            onChange={(e) => handleInputChange(index, 'bonus_speed', parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Descripción actual */}
                    <div className="bg-gray-50 p-3 rounded">
                      <h4 className="font-medium text-gray-800 mb-2">Descripción Actual:</h4>
                      <p className="text-sm text-gray-600 whitespace-pre-line">
                        {getModeDescription(mode)}
                      </p>
                    </div>

                    {/* Configuración actual */}
                    <div className="bg-blue-50 p-3 rounded">
                      <h4 className="font-medium text-blue-800 mb-2">Configuración:</h4>
                      <div className="text-sm text-blue-700 space-y-1">
                        {mode.isGlobalTimer ? (
                          <p>⏱️ Tiempo total: {mode.totalTime} segundos</p>
                        ) : (
                          <>
                            <p>⏰ Tiempo por pregunta: {mode.timePerQuestion} segundos</p>
                            <p>📝 Número de preguntas: {mode.numQuestions}</p>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Configuración de puntuación */}
                    <div className="bg-green-50 p-3 rounded">
                      <h4 className="font-medium text-green-800 mb-2">🎯 Puntuación:</h4>
                      <div className="text-sm text-green-700 space-y-1">
                        <p>✅ Correcta: {mode.points_correct || 100} puntos</p>
                        <p>❌ Incorrecta: {mode.points_incorrect || -25} puntos</p>
                        <p>🔥 Racha: +{mode.bonus_streak || 50} puntos (cada {mode.bonus_streak_threshold || 3} aciertos)</p>
                        {mode.bonus_perfect > 0 && (
                          <p>⭐ Perfecta: +{mode.bonus_perfect} puntos</p>
                        )}
                        {mode.bonus_speed > 0 && (
                          <p>⚡ Velocidad: +{mode.bonus_speed} puntos/segundo</p>
                        )}
                      </div>
                    </div>

                    {/* Estado de sincronización */}
                    <div className="bg-green-50 p-3 rounded">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-sm text-green-700">Sincronizado con el juego</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
      </div>

      {/* Información adicional */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-blue-800 mb-2">ℹ️ Información</h3>
        <div className="text-sm text-blue-700 space-y-2">
          <p>• Los cambios se aplican automáticamente al juego en tiempo real</p>
          <p>• El juego mostrará las nuevas configuraciones en las descripciones de los modos</p>
          <p>• Las preguntas se ajustarán según la nueva configuración</p>
          <p>• Los cambios se guardan en el archivo de configuración del sistema</p>
        </div>
      </div>
    </div>
  );
};

export default GameModesManagement; 