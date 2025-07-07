import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:5000/api';

const CategoriesManagement = () => {
  const [categories, setCategories] = useState([]);
  const [newCategory, setNewCategory] = useState('');
  const [editingCategory, setEditingCategory] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cleaning, setCleaning] = useState(false);
  const [cleanResult, setCleanResult] = useState(null);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/categories`);
      if (response.ok) {
        const data = await response.json();
        setCategories(data);
      } else {
        setError('Error al cargar las categorías');
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const addCategory = async () => {
    if (!newCategory.trim()) return;
    try {
      const response = await fetch(`${API_BASE_URL}/categories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newCategory.trim() })
      });
      if (response.ok) {
        setNewCategory('');
        loadCategories();
      } else {
        const data = await response.json();
        alert(data.error || 'Error al agregar categoría');
      }
    } catch (error) {
      alert('Error de conexión: ' + error.message);
    }
  };

  const startEdit = (cat) => {
    setEditingCategory(cat);
    setEditValue(cat);
  };

  const saveEdit = async () => {
    if (!editValue.trim()) return;
    try {
      const response = await fetch(`${API_BASE_URL}/categories/${editingCategory}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ newName: editValue.trim() })
      });
      if (response.ok) {
        setEditingCategory(null);
        setEditValue('');
        loadCategories();
      } else {
        const data = await response.json();
        alert(data.error || 'Error al editar categoría');
      }
    } catch (error) {
      alert('Error de conexión: ' + error.message);
    }
  };

  const deleteCategory = async (cat) => {
    if (!window.confirm('¿Eliminar la categoría?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/categories/${cat}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        loadCategories();
      } else {
        const data = await response.json();
        alert(data.error || 'Error al eliminar categoría');
      }
    } catch (error) {
      alert('Error de conexión: ' + error.message);
    }
  };

  const cleanOrphanQuestions = async () => {
    const token = window.prompt('Ingrese el token de administrador para limpiar preguntas huérfanas:');
    if (!token) return;
    setCleaning(true);
    setCleanResult(null);
    try {
      const response = await fetch(`${API_BASE_URL}/clean-orphan-questions`, {
        method: 'POST',
        headers: { 'X-Admin-Token': token }
      });
      const data = await response.json();
      if (data.success) {
        setCleanResult({ success: true, output: data.output });
        loadCategories(); // refrescar categorías si cambió algo
      } else {
        setCleanResult({ success: false, error: data.error });
      }
    } catch (error) {
      setCleanResult({ success: false, error: error.message });
    } finally {
      setCleaning(false);
    }
  };

  if (loading) {
    return <div className="p-6 bg-white rounded-xl shadow-lg m-6">Cargando categorías...</div>;
  }
  if (error) {
    return <div className="p-6 bg-white rounded-xl shadow-lg m-6 text-red-600">{error}</div>;
  }

  return (
    <div className="p-6 bg-white rounded-xl shadow-lg m-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Gestión de Categorías</h2>
      <div className="mb-6 flex gap-4">
        <input
          type="text"
          placeholder="Nueva categoría"
          value={newCategory}
          onChange={e => setNewCategory(e.target.value)}
          className="p-3 border border-gray-300 rounded-lg flex-1"
        />
        <button onClick={addCategory} className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">Agregar</button>
        <button
          onClick={cleanOrphanQuestions}
          className="bg-red-700 text-white px-6 py-2 rounded-lg hover:bg-red-800"
          disabled={cleaning}
        >
          {cleaning ? 'Limpiando...' : 'Limpiar preguntas huérfanas'}
        </button>
      </div>
      {cleanResult && (
        <div className={`mb-4 p-3 rounded-lg text-center ${cleanResult.success ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
          {cleanResult.success ? (
            <>
              <b>Limpieza completada:</b>
              <pre className="text-xs text-left whitespace-pre-wrap mt-2">{cleanResult.output}</pre>
            </>
          ) : (
            <>
              <b>Error:</b> {cleanResult.error}
            </>
          )}
        </div>
      )}
      <div className="overflow-y-auto" style={{maxHeight: '500px', overflowX: 'hidden'}}>
        <table className="w-full bg-white rounded-xl shadow-sm" style={{tableLayout: 'fixed'}}>
          <thead className="sticky top-0 bg-gray-100">
            <tr className="border-b border-gray-200 text-gray-600 uppercase text-xs leading-tight">
              <th className="py-1 px-1 text-left" style={{maxWidth: '120px'}}>Nombre</th>
              <th className="py-1 px-1 text-center" style={{maxWidth: '80px'}}>Acciones</th>
            </tr>
          </thead>
          <tbody className="text-gray-700 text-xs font-light">
            {categories.map((cat) => (
              <tr key={cat} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="py-0.5 px-1 text-left overflow-hidden text-ellipsis whitespace-nowrap" style={{maxWidth: '120px'}}>
                  {editingCategory === cat ? (
                    <input
                      type="text"
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      className="p-1 border border-gray-300 rounded-lg"
                    />
                  ) : (
                    cat
                  )}
                </td>
                <td className="py-0.5 px-1 text-center whitespace-nowrap" style={{maxWidth: '80px'}}>
                  {editingCategory === cat ? (
                    <>
                      <button onClick={saveEdit} className="bg-green-500 text-white px-1 py-0.5 rounded mr-1 text-xs">Guardar</button>
                      <button onClick={() => setEditingCategory(null)} className="bg-gray-400 text-white px-1 py-0.5 rounded text-xs">Cancelar</button>
                    </>
                  ) : (
                    <>
                      <button onClick={() => startEdit(cat)} className="bg-yellow-500 text-white px-1 py-0.5 rounded mr-1 text-xs">Editar</button>
                      <button onClick={() => deleteCategory(cat)} className="bg-red-500 text-white px-1 py-0.5 rounded text-xs">Eliminar</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CategoriesManagement; 