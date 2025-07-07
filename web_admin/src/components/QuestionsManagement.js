import React, { useState, useEffect } from 'react';
import Modal from './Modal';

const API_BASE_URL = 'http://localhost:5000/api';

const QuestionsManagement = () => {
  const [filter, setFilter] = useState({ mode: '', category: '', difficulty: '' });
  const [searchTerm, setSearchTerm] = useState('');
  const [questions, setQuestions] = useState([]);
  const [newQuestion, setNewQuestion] = useState({ text: '', mode: '', category: '', difficulty: 'Fácil', image: null, options: ['', '', '', ''], correctAnswer: '' });
  const [gameModes, setGameModes] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  
  // Estados para paginación
  const [currentPage, setCurrentPage] = useState(1);
  const [questionsPerPage] = useState(10);
  
  // Estados para exportación/importación
  const [isExporting, setIsExporting] = useState(false);
  const [isImporting, setIsImporting] = useState(false);
  
  // Estados para validaciones
  const [validationErrors, setValidationErrors] = useState({});

  // Cargar preguntas al montar el componente
  useEffect(() => {
    loadQuestions();
    loadGameModes();
  }, []);

  // Limpiar mensaje de éxito después de 3 segundos
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/questions`);
      if (response.ok) {
        const data = await response.json();
        setQuestions(data);
      } else {
        setError('Error al cargar las preguntas');
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const loadGameModes = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/game-modes`);
      if (response.ok) {
        const data = await response.json();
        setGameModes(data);
      }
    } catch (error) {
      console.error('Error cargando modos de juego:', error);
    }
  };

  const handleFilterChange = (e) => {
    setFilter({ ...filter, [e.target.name]: e.target.value });
  };

  const handleNewQuestionChange = (e) => {
    setNewQuestion({ ...newQuestion, [e.target.name]: e.target.value });
  };

  const handleOptionChange = (index, value) => {
    const updatedOptions = [...newQuestion.options];
    updatedOptions[index] = value;
    setNewQuestion({ ...newQuestion, options: updatedOptions });
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validar tipo de archivo
      if (!file.type.startsWith('image/')) {
        setError('Por favor selecciona un archivo de imagen válido');
        return;
      }
      
      // Validar tamaño (máximo 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('La imagen debe ser menor a 5MB');
        return;
      }

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          setNewQuestion({ ...newQuestion, image: data.url });
          setError(null);
        } else {
          setError('Error al subir la imagen');
        }
      } catch (error) {
        setError('Error de conexión al subir imagen');
      }
    }
  };

  const removeImage = () => {
    setNewQuestion({ ...newQuestion, image: null });
  };

  const addQuestion = async () => {
    try {
      const questionData = {
        text: newQuestion.text,
        mode: newQuestion.mode,
        category: newQuestion.category,
        difficulty: newQuestion.difficulty,
        options: newQuestion.options,
        correctAnswer: newQuestion.correctAnswer,
        image: newQuestion.image
      };

      const response = await fetch(`${API_BASE_URL}/questions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(questionData),
      });

      if (response.ok) {
        const data = await response.json();
        setQuestions([...questions, data.question]);
        setNewQuestion({ text: '', mode: '', category: '', difficulty: 'Fácil', image: null, options: ['', '', '', ''], correctAnswer: '' });
        setError(null);
        setSuccessMessage('Pregunta añadida exitosamente');
      } else {
        const errorData = await response.json();
        setError('Error al añadir pregunta: ' + errorData.error);
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    }
  };

  const deleteQuestion = async (id) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar esta pregunta?')) {
      try {
        const response = await fetch(`${API_BASE_URL}/questions/${id}`, {
          method: 'DELETE',
        });

        if (response.ok) {
          setQuestions(questions.filter(q => q.id !== id));
          setError(null);
          setSuccessMessage('Pregunta eliminada exitosamente');
        } else {
          const errorData = await response.json();
          setError('Error al eliminar pregunta: ' + errorData.error);
        }
      } catch (error) {
        setError('Error de conexión: ' + error.message);
      }
    }
  };

  const openEditModal = (question) => {
    setCurrentQuestion({
      id: question.id,
      text: question.text || question.pregunta || '',
      mode: question.mode || question.modo || '',
      category: question.category || question.categoria || '',
      difficulty: question.difficulty || question.dificultad || 'Fácil',
      image: question.image || question.imagen || null,
      options: question.options || question.opciones || ['', '', '', ''],
      correctAnswer: question.correctAnswer || question.respuesta || ''
    });
    setIsModalOpen(true);
  };

  const saveQuestionChanges = async () => {
    try {
      const questionData = {
        text: currentQuestion.text,
        mode: currentQuestion.mode,
        category: currentQuestion.category,
        difficulty: currentQuestion.difficulty,
        options: currentQuestion.options,
        correctAnswer: currentQuestion.correctAnswer,
        image: currentQuestion.image
      };

      const response = await fetch(`${API_BASE_URL}/questions/${currentQuestion.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(questionData),
      });

      if (response.ok) {
        const data = await response.json();
        setQuestions(questions.map(q => 
          q.id === currentQuestion.id ? data.question : q
        ));
        setIsModalOpen(false);
        setCurrentQuestion(null);
        setError(null);
        setSuccessMessage('Pregunta actualizada exitosamente');
      } else {
        const errorData = await response.json();
        setError('Error al actualizar pregunta: ' + errorData.error);
      }
    } catch (error) {
      setError('Error de conexión: ' + error.message);
    }
  };

  const handleModalQuestionChange = (e) => {
    setCurrentQuestion({ ...currentQuestion, [e.target.name]: e.target.value });
  };

  const handleModalOptionChange = (index, value) => {
    const updatedOptions = [...currentQuestion.options];
    updatedOptions[index] = value;
    setCurrentQuestion({ ...currentQuestion, options: updatedOptions });
  };

  const filteredQuestions = questions.filter(q => {
    const matchesSearch = searchTerm === '' || 
      (q.pregunta && q.pregunta.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (q.text && q.text.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesMode = filter.mode === '' || q.modo === filter.mode;
    const matchesCategory = filter.category === '' || q.categoria === filter.category;
    const matchesDifficulty = filter.difficulty === '' || q.dificultad === filter.difficulty;
    
    return matchesSearch && matchesMode && matchesCategory && matchesDifficulty;
  });

  // Obtener categorías y dificultades únicas de las preguntas
  const getCategories = () => {
    const categories = questions.map(q => q.category || q.categoria || '').filter(Boolean);
    return Array.from(new Set(categories));
  };
  const getDifficulties = () => {
    const difficulties = questions.map(q => q.difficulty || q.dificultad || '').filter(Boolean);
    return Array.from(new Set(difficulties));
  };

  // Funciones de paginación
  const indexOfLastQuestion = currentPage * questionsPerPage;
  const indexOfFirstQuestion = indexOfLastQuestion - questionsPerPage;
  const currentQuestions = filteredQuestions.slice(indexOfFirstQuestion, indexOfLastQuestion);
  const totalPages = Math.ceil(filteredQuestions.length / questionsPerPage);

  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  const goToPreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  // Resetear página cuando cambian los filtros
  useEffect(() => {
    setCurrentPage(1);
  }, [filter, searchTerm]);

  // Funciones de exportación/importación
  const exportQuestions = () => {
    setIsExporting(true);
    try {
      const dataStr = JSON.stringify(questions, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `preguntas_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      setSuccessMessage('Preguntas exportadas exitosamente');
    } catch (error) {
      setError('Error al exportar las preguntas');
    } finally {
      setIsExporting(false);
    }
  };

  const importQuestions = (event) => {
    const file = event.target.files[0];
    if (file) {
      setIsImporting(true);
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const importedQuestions = JSON.parse(e.target.result);
          if (Array.isArray(importedQuestions)) {
            // Validar que cada pregunta tenga los campos requeridos
            const validQuestions = importedQuestions.filter(q => 
              q.pregunta || q.text
            );
            
            if (validQuestions.length === 0) {
              setError('El archivo no contiene preguntas válidas');
              return;
            }
            
            // Agregar las preguntas importadas
            const newQuestions = [...questions, ...validQuestions];
            setQuestions(newQuestions);
            setSuccessMessage(`${validQuestions.length} preguntas importadas exitosamente`);
          } else {
            setError('Formato de archivo inválido');
          }
        } catch (error) {
          setError('Error al procesar el archivo');
        } finally {
          setIsImporting(false);
        }
      };
      reader.readAsText(file);
    }
  };

  // Funciones de validación
  const validateQuestion = (question) => {
    const errors = {};
    
    if (!question.text || question.text.trim().length < 10) {
      errors.text = 'La pregunta debe tener al menos 10 caracteres';
    }
    
    if (!question.category || question.category.trim().length === 0) {
      errors.category = 'La categoría es obligatoria';
    }
    
    if (!question.difficulty) {
      errors.difficulty = 'La dificultad es obligatoria';
    }
    
    const validOptions = question.options.filter(option => option && option.trim().length > 0);
    if (validOptions.length < 2) {
      errors.options = 'Debe haber al menos 2 opciones válidas';
    }
    
    if (!question.correctAnswer || question.correctAnswer.trim().length === 0) {
      errors.correctAnswer = 'La respuesta correcta es obligatoria';
    } else if (!validOptions.includes(question.correctAnswer)) {
      errors.correctAnswer = 'La respuesta correcta debe ser una de las opciones';
    }
    
    return errors;
  };

  const validateAndAddQuestion = async () => {
    const errors = validateQuestion(newQuestion);
    setValidationErrors(errors);
    
    if (Object.keys(errors).length === 0) {
      await addQuestion();
    }
  };

  const clearForm = () => {
    setNewQuestion({ text: '', mode: '', category: '', difficulty: 'Fácil', image: null, options: ['', '', '', ''], correctAnswer: '' });
    setValidationErrors({});
    setError(null);
  };

  if (loading) {
    return (
      <div className="p-6 bg-white rounded-xl shadow-lg m-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-xl text-gray-600">Cargando preguntas...</div>
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
            onClick={loadQuestions}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-xl shadow-lg m-6" style={{overflowX: 'hidden'}}>
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Gestión de Preguntas</h2>

      {/* Mensajes de éxito y error */}
      {successMessage && (
        <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded-lg">
          {successMessage}
        </div>
      )}
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <div className="mb-8 p-6 border border-gray-200 rounded-xl bg-gray-50">
        <h3 className="text-xl font-semibold mb-4 text-gray-700">Añadir Nueva Pregunta</h3>
        <input type="text" name="text" placeholder="Texto de la Pregunta" value={newQuestion.text} onChange={handleNewQuestionChange} className="w-full p-3 border border-gray-300 rounded-lg mb-3 focus:ring-2 focus:ring-blue-500" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
          <select
            name="mode"
            value={newQuestion.mode}
            onChange={handleNewQuestionChange}
            className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Modo</option>
            {gameModes.map(mode => (
              <option key={mode.name} value={mode.name}>{mode.name}</option>
            ))}
          </select>
          <select
            name="category"
            value={newQuestion.category}
            onChange={handleNewQuestionChange}
            className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Categoría</option>
            {getCategories().map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          <select name="difficulty" value={newQuestion.difficulty} onChange={handleNewQuestionChange} className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
            <option value="Fácil">Fácil</option>
            <option value="Medio">Medio</option>
            <option value="Difícil">Difícil</option>
          </select>
        </div>
        <div className="mb-3">
          <label className="block text-gray-700 text-sm font-bold mb-2">Opciones de Respuesta (4):</label>
          {newQuestion.options.map((option, index) => (
            <input
              key={index}
              type="text"
              value={option}
              onChange={(e) => handleOptionChange(index, e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg mb-2 focus:ring-2 focus:ring-blue-500"
              placeholder={`Opción ${index + 1}`}
            />
          ))}
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Respuesta Correcta:</label>
          <select
            value={newQuestion.correctAnswer}
            onChange={(e) => setNewQuestion({ ...newQuestion, correctAnswer: e.target.value })}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Selecciona la correcta</option>
            {newQuestion.options.map((option, index) => (
              option && <option key={index} value={option}>{option}</option>
            ))}
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Imagen (opcional):</label>
          <div className="flex items-center space-x-4">
            <input 
              type="file" 
              accept="image/*" 
              onChange={handleImageUpload} 
              className="flex-1 p-3 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500" 
            />
            {newQuestion.image && (
              <button
                onClick={removeImage}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                Eliminar
              </button>
            )}
          </div>
          {newQuestion.image && (
            <div className="mt-3 p-3 border border-gray-300 rounded-lg bg-gray-50">
              <p className="text-sm text-gray-600 mb-2">Vista previa:</p>
              <img 
                src={newQuestion.image} 
                alt="Vista previa" 
                className="w-32 h-32 object-cover rounded-lg border border-gray-300" 
              />
            </div>
          )}
        </div>
        <div className="flex gap-3">
          <button onClick={validateAndAddQuestion} className="flex-1 py-3 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 transition-colors">
            Añadir Pregunta
          </button>
          <button onClick={clearForm} className="px-6 py-3 bg-gray-500 text-white rounded-lg shadow-md hover:bg-gray-600 transition-colors">
            Limpiar
          </button>
        </div>
      </div>

      {/* Filtros de búsqueda */}
      <div className="mb-6 p-4 border border-gray-200 rounded-xl bg-gray-50">
        <h3 className="text-lg font-semibold mb-4 text-gray-700">Filtrar y Buscar Preguntas</h3>
        
        {/* Campo de búsqueda */}
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">Buscar por texto:</label>
          <input
            type="text"
            placeholder="Buscar en el texto de las preguntas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        {/* Filtros */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">Modo:</label>
            <select name="mode" value={filter.mode} onChange={handleFilterChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
              <option value="">Todos los modos</option>
              {gameModes.map(mode => <option key={mode.name} value={mode.name}>{mode.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">Categoría:</label>
            <select name="category" value={filter.category} onChange={handleFilterChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
              <option value="">Todas las categorías</option>
              {getCategories().map(cat => <option key={cat} value={cat}>{cat}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">Dificultad:</label>
            <select name="difficulty" value={filter.difficulty} onChange={handleFilterChange} className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
              <option value="">Todas las dificultades</option>
              {getDifficulties().map(diff => <option key={diff} value={diff}>{diff}</option>)}
            </select>
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-blue-700 text-sm">
            <strong>Resultados:</strong> {filteredQuestions.length} pregunta{filteredQuestions.length !== 1 ? 's' : ''} encontrada{filteredQuestions.length !== 1 ? 's' : ''}
            {searchTerm && <span> para "{searchTerm}"</span>}
          </p>
        </div>
      </div>

      {/* Tabla de preguntas sin scroll vertical, solo paginación */}
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded-xl shadow-sm">
          <thead className="sticky top-0 bg-gray-100">
            <tr className="border-b border-gray-200 text-gray-600 uppercase text-xs leading-tight">
              <th className="py-1 px-1 text-left">ID</th>
              <th className="py-1 px-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">Pregunta</th>
              <th className="py-1 px-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">Modo</th>
              <th className="py-1 px-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">Categoría</th>
              <th className="py-1 px-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">Dificultad</th>
              <th className="py-1 px-1 text-center">Img</th>
              <th className="py-1 px-1 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody className="text-gray-700 text-xs font-light">
            {currentQuestions.map((q) => (
              <tr key={q.id} className="border-b border-gray-200 hover:bg-gray-50">
                <td className="py-0.5 px-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">{q.id}</td>
                <td className="py-0.5 px-1 text-left whitespace-nowrap overflow-hidden text-ellipsis" title={q.pregunta || q.text || ''}>{q.pregunta || q.text || ''}</td>
                <td className="py-0.5 px-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">{q.modo || q.mode || ''}</td>
                <td className="py-0.5 px-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">{q.categoria || q.category || ''}</td>
                <td className="py-0.5 px-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">{q.dificultad || q.difficulty || ''}</td>
                <td className="py-0.5 px-1 text-center">{q.imagen || q.image ? <img src={q.imagen || q.image} alt="Pregunta" className="w-5 h-5 object-cover rounded-md mx-auto" /> : 'N/A'}</td>
                <td className="py-0.5 px-1 text-center whitespace-nowrap">
                  <button onClick={() => openEditModal(q)} className="bg-blue-500 text-white py-0.5 px-1 rounded-md hover:bg-blue-600 transition-colors mr-1 text-xs">Editar</button>
                  <button onClick={() => deleteQuestion(q.id)} className="bg-red-500 text-white py-0.5 px-1 rounded-md hover:bg-red-600 transition-colors text-xs">Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Controles de paginación */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Mostrando {indexOfFirstQuestion + 1} a {Math.min(indexOfLastQuestion, filteredQuestions.length)} de {filteredQuestions.length} preguntas
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={goToPreviousPage}
              disabled={currentPage === 1}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Anterior
            </button>
            {/* Paginación profesional con puntos suspensivos */}
            {(() => {
              const pageButtons = [];
              const pageRange = 2; // Cuántos botones a cada lado de la actual
              let start = Math.max(2, currentPage - pageRange);
              let end = Math.min(totalPages - 1, currentPage + pageRange);
              // Primer página
              pageButtons.push(
              <button
                  key={1}
                  onClick={() => paginate(1)}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${currentPage === 1 ? 'bg-blue-600 text-white' : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50'}`}
              >
                  1
              </button>
              );
              // Puntos suspensivos si es necesario
              if (start > 2) {
                pageButtons.push(<span key="start-ellipsis" className="px-2">...</span>);
              }
              // Botones intermedios
              for (let i = start; i <= end; i++) {
                pageButtons.push(
                  <button
                    key={i}
                    onClick={() => paginate(i)}
                    className={`px-3 py-2 text-sm font-medium rounded-md ${currentPage === i ? 'bg-blue-600 text-white' : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50'}`}
                  >
                    {i}
                  </button>
                );
              }
              // Puntos suspensivos si es necesario
              if (end < totalPages - 1) {
                pageButtons.push(<span key="end-ellipsis" className="px-2">...</span>);
              }
              // Última página
              if (totalPages > 1) {
                pageButtons.push(
                  <button
                    key={totalPages}
                    onClick={() => paginate(totalPages)}
                    className={`px-3 py-2 text-sm font-medium rounded-md ${currentPage === totalPages ? 'bg-blue-600 text-white' : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-50'}`}
                  >
                    {totalPages}
                  </button>
                );
              }
              return pageButtons;
            })()}
            <button
              onClick={goToNextPage}
              disabled={currentPage === totalPages}
              className="px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Siguiente
            </button>
          </div>
        </div>
      )}

      {/* Herramientas de datos */}
      <div className="mt-8 p-6 border border-gray-200 rounded-xl bg-gray-50">
        <h3 className="text-xl font-semibold mb-4 text-gray-700">Herramientas de Datos</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border border-gray-300 rounded-lg bg-white">
            <h4 className="text-lg font-semibold mb-2 text-gray-700">Exportar Preguntas</h4>
            <p className="text-sm text-gray-600 mb-3">Descarga todas las preguntas en formato JSON</p>
            <button 
              onClick={exportQuestions}
              disabled={isExporting}
              className="w-full py-2 bg-purple-600 text-white rounded-lg shadow-md hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              {isExporting ? 'Exportando...' : 'Exportar (JSON)'}
            </button>
          </div>
          
          <div className="p-4 border border-gray-300 rounded-lg bg-white">
            <h4 className="text-lg font-semibold mb-2 text-gray-700">Importar Preguntas</h4>
            <p className="text-sm text-gray-600 mb-3">Importa preguntas desde un archivo JSON</p>
            <input
              type="file"
              accept=".json"
              onChange={importQuestions}
              disabled={isImporting}
              className="w-full p-2 border border-gray-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
            {isImporting && <p className="text-sm text-blue-600 mt-2">Importando...</p>}
          </div>
        </div>
      </div>

      {isModalOpen && currentQuestion && (
        <Modal onClose={() => setIsModalOpen(false)}>
          <div className="max-w-2xl mx-auto">
            <h3 className="text-xl font-bold mb-4 text-gray-800">Editar Pregunta</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-gray-700 text-sm font-bold mb-2">Texto de la Pregunta:</label>
                <textarea 
                  name="text" 
                  value={currentQuestion.text} 
                  onChange={handleModalQuestionChange} 
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
                  rows="3"
                />
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-gray-700 text-sm font-bold mb-1">Modo:</label>
                  <select name="mode" value={currentQuestion.mode} onChange={handleModalQuestionChange} className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    <option value="">Seleccionar modo</option>
                    {gameModes.map(mode => <option key={mode.name} value={mode.name}>{mode.name}</option>)}
                  </select>
                </div>
                
                <div>
                  <label className="block text-gray-700 text-sm font-bold mb-1">Categoría:</label>
                  <input type="text" name="category" value={currentQuestion.category} onChange={handleModalQuestionChange} className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500" />
                </div>
                
                <div>
                  <label className="block text-gray-700 text-sm font-bold mb-1">Dificultad:</label>
                  <select name="difficulty" value={currentQuestion.difficulty} onChange={handleModalQuestionChange} className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                    <option value="Fácil">Fácil</option>
                    <option value="Medio">Medio</option>
                    <option value="Difícil">Difícil</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">Opciones de Respuesta:</label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {currentQuestion.options.map((option, index) => (
                  <input
                    key={index}
                    type="text"
                    value={option}
                    onChange={(e) => handleModalOptionChange(index, e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder={`Opción ${index + 1}`}
                  />
                ))}
              </div>
            </div>
            
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2">Respuesta Correcta:</label>
              <select
                value={currentQuestion.correctAnswer}
                onChange={(e) => setCurrentQuestion({ ...currentQuestion, correctAnswer: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Selecciona la correcta</option>
                {currentQuestion.options.map((option, index) => (
                  option && <option key={index} value={option}>{option}</option>
                ))}
              </select>
            </div>
            
            <div className="flex gap-2">
              <button onClick={saveQuestionChanges} className="flex-1 py-2 bg-green-600 text-white rounded-lg shadow-md hover:bg-green-700 transition-colors">
                Guardar Cambios
              </button>
              <button onClick={() => setIsModalOpen(false)} className="px-4 py-2 bg-gray-500 text-white rounded-lg shadow-md hover:bg-gray-600 transition-colors">
                Cancelar
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default QuestionsManagement;