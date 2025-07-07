import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';

const VisualEditor = () => {
  const [categories, setCategories] = useState([]);
  const [categoryColors, setCategoryColors] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');
  const [buttonStyles, setButtonStyles] = useState({});

  // Cargar categorías y colores desde la API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Cargar categorías
        const categoriesResponse = await fetch('http://localhost:5000/api/categories');
        const categoriesData = await categoriesResponse.json();
        setCategories(categoriesData);

        // Cargar colores de categorías
        const colorsResponse = await fetch('http://localhost:5000/api/category-colors');
        const colorsData = await colorsResponse.json();
        setCategoryColors(colorsData);

        // Cargar estilos de botones
        const buttonStylesResponse = await fetch('http://localhost:5000/api/button-styles');
        const buttonStylesData = await buttonStylesResponse.json();
        setButtonStyles(buttonStylesData);

      } catch (error) {
        console.error('Error cargando datos:', error);
        setError('Error cargando datos');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Escuchar actualizaciones en tiempo real
  useEffect(() => {
    const socket = io();

    socket.on('data_update', (data) => {
      if (data.type === 'categories') {
        fetch('http://localhost:5000/api/categories')
          .then(res => res.json())
          .then(setCategories)
          .catch(console.error);
      } else if (data.type === 'category_colors') {
        fetch('http://localhost:5000/api/category-colors')
          .then(res => res.json())
          .then(setCategoryColors)
          .catch(console.error);
      } else if (data.type === 'button_styles') {
        fetch('http://localhost:5000/api/button-styles')
          .then(res => res.json())
          .then(setButtonStyles)
          .catch(console.error);
      }
    });

    return () => socket.disconnect();
  }, []);

  const saveCategoryColors = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/category-colors', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(categoryColors),
      });

      if (response.ok) {
        setMessage('Colores de categorías guardados correctamente');
        setTimeout(() => setMessage(''), 3000);
      } else {
        const errorData = await response.json();
        setError('Error al guardar colores de categorías: ' + errorData.error);
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    }
  };

  const saveButtonStyles = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/button-styles', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(buttonStyles),
      });

      if (response.ok) {
        setMessage('Estilos de botones guardados correctamente');
        setTimeout(() => setMessage(''), 3000);
      } else {
        const errorData = await response.json();
        setError('Error al guardar estilos de botones: ' + errorData.error);
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    }
  };

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-xl shadow-lg m-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-gray-600">Cargando datos...</div>
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
            onClick={() => window.location.reload()}
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
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Editor Visual</h2>

      {message && (
        <div className={`mb-4 p-3 rounded-lg text-center ${
          message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
        }`}>
          {message}
        </div>
      )}

      {/* Sección de Colores por Categoría */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4 text-gray-800">Colores por Categoría</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categories.map((category) => (
            <div key={category} className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium text-gray-700 mb-3">{category}</h4>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Color de Fondo</label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="color"
                      value={categoryColors[category]?.bg_color || '#3498db'}
                      onChange={(e) => {
                        const newColors = { ...categoryColors };
                        if (!newColors[category]) {
                          newColors[category] = {};
                        }
                        newColors[category].bg_color = e.target.value;
                        setCategoryColors(newColors);
                      }}
                      className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={categoryColors[category]?.bg_color || '#3498db'}
                      onChange={(e) => {
                        const newColors = { ...categoryColors };
                        if (!newColors[category]) {
                          newColors[category] = {};
                        }
                        newColors[category].bg_color = e.target.value;
                        setCategoryColors(newColors);
                      }}
                      className="flex-1 p-2 border border-gray-300 rounded-md text-sm"
                      placeholder="#3498db"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-gray-600 mb-1">Color Hover</label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="color"
                      value={categoryColors[category]?.hover_color || '#2980b9'}
                      onChange={(e) => {
                        const newColors = { ...categoryColors };
                        if (!newColors[category]) {
                          newColors[category] = {};
                        }
                        newColors[category].hover_color = e.target.value;
                        setCategoryColors(newColors);
                      }}
                      className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={categoryColors[category]?.hover_color || '#2980b9'}
                      onChange={(e) => {
                        const newColors = { ...categoryColors };
                        if (!newColors[category]) {
                          newColors[category] = {};
                        }
                        newColors[category].hover_color = e.target.value;
                        setCategoryColors(newColors);
                      }}
                      className="flex-1 p-2 border border-gray-300 rounded-md text-sm"
                      placeholder="#2980b9"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-gray-600 mb-1">Color del Texto</label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="color"
                      value={categoryColors[category]?.text_color || 'white'}
                      onChange={(e) => {
                        const newColors = { ...categoryColors };
                        if (!newColors[category]) {
                          newColors[category] = {};
                        }
                        newColors[category].text_color = e.target.value;
                        setCategoryColors(newColors);
                      }}
                      className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
                    />
                    <input
                      type="text"
                      value={categoryColors[category]?.text_color || 'white'}
                      onChange={(e) => {
                        const newColors = { ...categoryColors };
                        if (!newColors[category]) {
                          newColors[category] = {};
                        }
                        newColors[category].text_color = e.target.value;
                        setCategoryColors(newColors);
                      }}
                      className="flex-1 p-2 border border-gray-300 rounded-md text-sm"
                      placeholder="white"
                    />
                  </div>
                </div>
              </div>

              {/* Vista Previa */}
              <div className="mt-4 p-3 rounded-lg text-center text-sm font-medium transition-colors duration-200"
                   style={{
                     backgroundColor: categoryColors[category]?.bg_color || '#3498db',
                     color: categoryColors[category]?.text_color || 'white'
                   }}
                   onMouseEnter={(e) => {
                     e.target.style.backgroundColor = categoryColors[category]?.hover_color || '#2980b9';
                   }}
                   onMouseLeave={(e) => {
                     e.target.style.backgroundColor = categoryColors[category]?.bg_color || '#3498db';
                   }}>
                Vista Previa
              </div>
            </div>
          ))}
        </div>

        {/* Botón de Guardar */}
        <div className="mt-6">
          <button
            onClick={saveCategoryColors}
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200"
          >
            Guardar Colores de Categorías
          </button>
        </div>
      </div>

      {/* Sección de Estilos de Botones */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4 text-gray-800">Estilos de Botones</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Forma del Botón */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Forma del Botón
            </label>
            <select
              value={buttonStyles.button_shape || 'rounded-lg'}
              onChange={(e) => setButtonStyles(prev => ({...prev, button_shape: e.target.value}))}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="rounded-lg">Redondeado</option>
              <option value="rounded-full">Circular</option>
              <option value="rounded-none">Cuadrado</option>
            </select>
          </div>

          {/* Color del Botón */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Color del Botón
            </label>
            <div className="flex items-center space-x-2">
            <input
              type="color"
                value={buttonStyles.button_color || '#3498db'}
                onChange={(e) => setButtonStyles(prev => ({...prev, button_color: e.target.value}))}
                className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
              />
              <input
                type="text"
                value={buttonStyles.button_color || '#3498db'}
                onChange={(e) => setButtonStyles(prev => ({...prev, button_color: e.target.value}))}
                className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="#3498db"
            />
          </div>
        </div>

          {/* Color del Texto */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Color del Texto
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="color"
                value={buttonStyles.button_text_color || 'white'}
                onChange={(e) => setButtonStyles(prev => ({...prev, button_text_color: e.target.value}))}
                className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
              />
              <input
                type="text"
                value={buttonStyles.button_text_color || 'white'}
                onChange={(e) => setButtonStyles(prev => ({...prev, button_text_color: e.target.value}))}
                className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="white"
              />
            </div>
          </div>

          {/* Color Hover */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Color Hover
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="color"
                value={buttonStyles.button_hover_color || '#2980b9'}
                onChange={(e) => setButtonStyles(prev => ({...prev, button_hover_color: e.target.value}))}
                className="w-12 h-10 border border-gray-300 rounded cursor-pointer"
              />
              <input
                type="text"
                value={buttonStyles.button_hover_color || '#2980b9'}
                onChange={(e) => setButtonStyles(prev => ({...prev, button_hover_color: e.target.value}))}
                className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="#2980b9"
              />
            </div>
          </div>

          {/* Ancho del Borde */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ancho del Borde
            </label>
            <input
              type="number"
              min="0"
              max="10"
              value={buttonStyles.button_border_width || 0}
              onChange={(e) => setButtonStyles(prev => ({...prev, button_border_width: parseInt(e.target.value)}))}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Relieve */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Relieve
            </label>
            <select
              value={buttonStyles.button_relief || 'flat'}
              onChange={(e) => setButtonStyles(prev => ({...prev, button_relief: e.target.value}))}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="flat">Plano</option>
              <option value="raised">Elevado</option>
              <option value="sunken">Hundido</option>
              <option value="groove">Surco</option>
              <option value="ridge">Cresta</option>
            </select>
        </div>
      </div>

        {/* Botón de Guardar */}
        <div className="mt-6">
          <button
            onClick={saveButtonStyles}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200"
          >
            Guardar Estilos de Botones
          </button>
        </div>

        {/* Vista Previa */}
        <div className="mt-6">
          <h4 className="text-lg font-medium text-gray-700 mb-3">Vista Previa</h4>
          <div className="flex space-x-4">
            <button
              className={`px-6 py-3 font-medium transition-colors duration-200 ${
                buttonStyles.button_shape === 'rounded-lg' ? 'rounded-lg' :
                buttonStyles.button_shape === 'rounded-full' ? 'rounded-full' :
                'rounded-none'
              }`}
              style={{
                backgroundColor: buttonStyles.button_color || '#3498db',
                color: buttonStyles.button_text_color || 'white',
                borderWidth: buttonStyles.button_border_width || 0
              }}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = buttonStyles.button_hover_color || '#2980b9';
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = buttonStyles.button_color || '#3498db';
              }}
            >
              Botón de Ejemplo
            </button>
        </div>
        </div>
      </div>
    </div>
  );
};

export default VisualEditor;