import React from 'react';

const LayoutSidebar = ({ currentPage, setCurrentPage, adminName }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'questions', label: 'Preguntas', icon: '❓' },
    { id: 'categories', label: 'Categorías', icon: '📚' },
    { id: 'gameModes', label: 'Modos de Juego', icon: '🎮' },
    { id: 'players', label: 'Jugadores', icon: '👥' },
    { id: 'ranking', label: 'Ranking', icon: '🏆' },
    { id: 'resources', label: 'Recursos', icon: '📁' },
    { id: 'settings', label: 'Configuración', icon: '⚙️' },
    { id: 'visual-editor', label: 'Editor Visual', icon: '🎨' },
    { id: 'errors', label: 'Reportes de Error', icon: '🐛' }
  ];

  return (
    <aside className="h-full w-64 bg-gradient-to-b from-blue-900 to-blue-800 shadow-xl flex flex-col">
      {/* Header compacto con ícono de panel */}
      <div className="flex items-center gap-3 px-6 py-6 border-b border-blue-700">
        <div className="bg-blue-700 rounded-lg w-10 h-10 flex items-center justify-center text-2xl text-white shadow-md">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor"><rect x="3" y="4" width="18" height="16" rx="3" strokeWidth="2" stroke="currentColor" fill="none"/><rect x="7" y="8" width="3" height="3" rx="1" fill="currentColor"/><rect x="14" y="8" width="3" height="3" rx="1" fill="currentColor"/><rect x="7" y="14" width="10" height="2" rx="1" fill="currentColor"/></svg>
        </div>
        <span className="text-xl font-bold text-white tracking-wide">Panel de Administración</span>
      </div>
      {/* Menú */}
      <nav className="flex-1 py-6 flex flex-col gap-1">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setCurrentPage(item.id)}
            className={`flex items-center gap-3 px-6 py-3 text-base font-medium transition-all rounded-l-full border-l-4
              ${currentPage === item.id
                ? 'bg-blue-700 text-white border-blue-300 shadow-lg'
                : 'text-blue-100 border-transparent hover:bg-blue-800 hover:text-white hover:border-blue-400'}
            `}
          >
            <span className="text-xl w-7 text-center">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
};

export default LayoutSidebar;