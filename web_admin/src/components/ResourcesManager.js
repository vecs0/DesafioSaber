import React, { useState, useEffect, useRef } from 'react';

const API_BASE_URL = 'http://localhost:5000/api';

const ResourcesManager = () => {
  const [sounds, setSounds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null);
  const audioRefs = useRef({});

  useEffect(() => {
    loadSounds();
  }, []);

  const loadSounds = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/sounds`);
      if (response.ok) {
        const data = await response.json();
        setSounds(data);
      } else {
        setError('Error al cargar los sonidos');
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAudioUpload = async (e) => {
    if (!e.target.files[0]) return;
    setUploading(true);
    setMessage('');
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch(`${API_BASE_URL}/sounds`, {
        method: 'POST',
        body: formData
      });
      if (response.ok) {
        setMessage('Sonido subido correctamente.');
        loadSounds();
      } else {
        setMessage('Error al subir el sonido.');
      }
    } catch (error) {
      setMessage('Error de conexión al subir sonido.');
    } finally {
      setUploading(false);
      e.target.value = null;
    }
  };

  const deleteSound = async (filename) => {
    if (!window.confirm('¿Eliminar este sonido?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/sounds/${filename}`, { method: 'DELETE' });
      if (response.ok) {
        setMessage('Sonido eliminado correctamente.');
        loadSounds();
      } else {
        setMessage('Error al eliminar el sonido.');
      }
    } catch (error) {
      setMessage('Error de conexión al eliminar sonido.');
    }
  };

  const playSound = (soundName, soundPath) => {
    // Detener cualquier sonido que esté reproduciéndose
    if (currentlyPlaying && audioRefs.current[currentlyPlaying]) {
      audioRefs.current[currentlyPlaying].pause();
      audioRefs.current[currentlyPlaying].currentTime = 0;
    }

    // Reproducir el nuevo sonido
    if (audioRefs.current[soundName]) {
      audioRefs.current[soundName].play();
      setCurrentlyPlaying(soundName);
      
      // Limpiar el estado cuando termine de reproducirse
      audioRefs.current[soundName].onended = () => {
        setCurrentlyPlaying(null);
      };
    }
  };

  const stopSound = (soundName) => {
    if (audioRefs.current[soundName]) {
      audioRefs.current[soundName].pause();
      audioRefs.current[soundName].currentTime = 0;
      setCurrentlyPlaying(null);
    }
  };

  const getAudioUrl = (soundPath) => {
    if (soundPath.startsWith('http')) return soundPath;
    // Usar la URL absoluta del backend
    return `http://localhost:5000${soundPath}`;
  };

  if (loading) {
    return <div className="p-6 bg-white rounded-xl shadow-lg m-6">Cargando sonidos...</div>;
  }
  if (error) {
    return <div className="p-6 bg-white rounded-xl shadow-lg m-6 text-red-600">{error}</div>;
  }

  return (
    <div className="p-6 bg-white rounded-xl shadow-lg m-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Gestión de Sonidos del Juego</h2>
      
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="text-lg font-semibold mb-2 text-blue-800">Instrucciones</h3>
        <p className="text-blue-700 text-sm">
          • Sube archivos de audio (MP3, WAV) para usar en el juego<br/>
          • Haz clic en "Reproducir" para escuchar el sonido<br/>
          • Solo se puede reproducir un sonido a la vez para evitar superposición
        </p>
      </div>
      
      <div className="mb-6 flex gap-4 items-center">
        <input type="file" accept="audio/*" onChange={handleAudioUpload} disabled={uploading} className="p-3 border border-gray-300 rounded-lg" />
        {uploading && <span className="text-blue-600">Subiendo...</span>}
        {message && <span className="text-green-600">{message}</span>}
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded-xl shadow-sm">
          <thead>
            <tr className="bg-gray-100 border-b border-gray-200 text-gray-600 uppercase text-sm leading-normal">
              <th className="py-3 px-6 text-left">Nombre</th>
              <th className="py-3 px-6 text-center">Controles de Audio</th>
              <th className="py-3 px-6 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody className="text-gray-700 text-sm font-light">
            {sounds.map((sound) => (
              <tr key={sound.name} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="py-3 px-6 text-left whitespace-nowrap">
                  <div className="flex items-center">
                    <span className="font-medium">{sound.name}</span>
                    {currentlyPlaying === sound.name && (
                      <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                        Reproduciendo
                      </span>
                    )}
                  </div>
                </td>
                <td className="py-3 px-6 text-center">
                  <div className="flex items-center justify-center space-x-2">
                    <audio
                      ref={(el) => audioRefs.current[sound.name] = el}
                      src={getAudioUrl(sound.path)}
                      preload="metadata"
                      className="hidden"
                      onError={() => setMessage(`No se puede reproducir el archivo: ${sound.name}`)}
                      onLoadedData={() => setMessage('')}
                    />
                    <button
                      onClick={() => playSound(sound.name, sound.path)}
                      disabled={currentlyPlaying === sound.name}
                      className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                        currentlyPlaying === sound.name
                          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                          : 'bg-blue-500 text-white hover:bg-blue-600'
                      }`}
                    >
                      {currentlyPlaying === sound.name ? 'Reproduciendo...' : 'Reproducir'}
                    </button>
                    {currentlyPlaying === sound.name && (
                      <button
                        onClick={() => stopSound(sound.name)}
                        className="px-3 py-1 bg-red-500 text-white rounded-md text-sm font-medium hover:bg-red-600 transition-colors"
                      >
                        Detener
                      </button>
                    )}
                  </div>
                </td>
                <td className="py-3 px-6 text-center">
                  <button 
                    onClick={() => deleteSound(sound.name)} 
                    className="bg-red-500 text-white py-1 px-3 rounded-md hover:bg-red-600 transition-colors"
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {sounds.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No hay sonidos disponibles. Sube algunos archivos de audio para comenzar.</p>
        </div>
      )}
    </div>
  );
};

export default ResourcesManager;