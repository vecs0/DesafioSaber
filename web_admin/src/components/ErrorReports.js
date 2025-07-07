import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:5000/api';

const ErrorReports = () => {
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadErrors();
  }, []);

  const loadErrors = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/errors`);
      if (response.ok) {
        const data = await response.json();
        setErrors(data);
      } else {
        setError('Error al cargar los errores: ' + response.statusText);
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const updateErrorStatus = async (errorId, newStatus) => {
    try {
      const response = await fetch(`${API_BASE_URL}/errors/${errorId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        setErrors(errors.map(err => 
          err.id === errorId ? { ...err, status: newStatus } : err
        ));
      } else {
        alert('Error al actualizar el estado del error');
      }
    } catch (error) {
      alert('Error de conexión: ' + error.message);
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString('es-ES');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pendiente':
        return 'bg-yellow-100 text-yellow-800';
      case 'en_proceso':
        return 'bg-blue-100 text-blue-800';
      case 'resuelto':
        return 'bg-green-100 text-green-800';
      case 'cerrado':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <strong>Error:</strong> {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Reportes de Errores</h2>
        <button
          onClick={loadErrors}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
        >
          🔄 Actualizar
        </button>
      </div>

      {errors.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🐛</div>
          <h3 className="text-xl font-semibold text-gray-600 mb-2">
            No hay errores reportados
          </h3>
          <p className="text-gray-500">
            Los errores reportados desde el juego aparecerán aquí
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {errors.map((error) => (
            <div key={error.id} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    Error #{error.id} - {error.name}
                  </h3>
                  <p className="text-sm text-gray-500">
                    Reportado el {formatDate(error.timestamp)}
                  </p>
                  <p className="text-sm text-gray-500">
                    Versión: {error.version}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(error.status)}`}>
                    {error.status}
                  </span>
                  <select
                    value={error.status}
                    onChange={(e) => updateErrorStatus(error.id, e.target.value)}
                    className="text-sm border border-gray-300 rounded px-2 py-1"
                  >
                    <option value="pendiente">Pendiente</option>
                    <option value="en_proceso">En Proceso</option>
                    <option value="resuelto">Resuelto</option>
                    <option value="cerrado">Cerrado</option>
                  </select>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Descripción del Error:</h4>
                <p className="text-gray-700 whitespace-pre-wrap">
                  {error.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ErrorReports; 