import React, { useState, useEffect } from 'react';
import LayoutSidebar from './components/LayoutSidebar';
import LayoutHeader from './components/LayoutHeader';
import DashboardOverview from './components/DashboardOverview';
import QuestionsManagement from './components/QuestionsManagement';
import PlayersManagement from './components/PlayersManagement';
import VisualEditor from './components/VisualEditor';
import RankingDisplay from './components/RankingDisplay';
import SettingsPanel from './components/SettingsPanel';
import ResourcesManager from './components/ResourcesManager';
import ErrorReports from './components/ErrorReports';
import AuthLogin from './components/AuthLogin';
import CategoriesManagement from './components/CategoriesManagement';
import PlayerStats from './components/PlayerStats';
import GameModesManagement from './components/GameModesManagement';

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [adminName, setAdminName] = useState('');
  const [adminImage, setAdminImage] = useState(null);
  const [adminUsername, setAdminUsername] = useState('');
  const [showAdminNameInput, setShowAdminNameInput] = useState(true); 

  const pageTitles = {
    dashboard: 'Inicio',
    questions: 'Preguntas',
    players: 'Jugadores',
    editor: 'Editor Visual',
    ranking: 'Ranking',
    settings: 'Configuración',
    resources: 'Recursos',
    errors: 'Errores',
    categories: 'Categorías',
    gameModes: 'Modos de Juego',
    // playerStats: 'Estadísticas del Jugador',
  };

  useEffect(() => {
    const storedAdminName = localStorage.getItem('adminName');
    const isAuthenticated = localStorage.getItem('isAuthenticated');
    
    if (storedAdminName && isAuthenticated === 'true') {
      setAdminName(storedAdminName);
      setAdminUsername(localStorage.getItem('adminUsername'));
      setIsLoggedIn(true);
      setShowAdminNameInput(false); 
    }
  }, []);

  const handleLogin = async (name, username) => {
    setIsLoggedIn(true);
    setAdminName(name);
    setAdminUsername(username);
    localStorage.setItem('adminName', name);
    localStorage.setItem('adminUsername', username);
    localStorage.setItem('isAuthenticated', 'true');
    setShowAdminNameInput(false);
    // Buscar imagen del admin
    try {
      const res = await fetch('http://localhost:5000/api/admin-users');
      if (res.ok) {
        const data = await res.json();
        const user = data.users.find(u => u.fullName === name || u.username === username);
        if (user && user.image) setAdminImage(user.image);
        else setAdminImage(null);
      }
    } catch {
      setAdminImage(null);
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentPage('dashboard');
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('adminName');
    localStorage.removeItem('adminUsername');
    setAdminImage(null);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardOverview />;
      case 'questions':
        return <QuestionsManagement />;
      case 'players':
        return <PlayersManagement />;
      case 'visual-editor':
        return <VisualEditor />;
      case 'ranking':
        return <RankingDisplay />;
      case 'settings':
        return <SettingsPanel />;
      case 'resources':
        return <ResourcesManager />;
      case 'errors':
        return <ErrorReports />;
      case 'categories':
        return <CategoriesManagement />;
      case 'gameModes':
        return <GameModesManagement />;
      // case 'playerStats':
      //   return <PlayerStats />;
      default:
        return <DashboardOverview />;
    }
  };

  if (!isLoggedIn) {
    return <AuthLogin onLogin={handleLogin} showAdminNameInput={showAdminNameInput} />;
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="fixed left-0 top-0 h-screen w-64 z-20">
        <LayoutSidebar currentPage={currentPage} setCurrentPage={setCurrentPage} adminName={adminName} />
      </div>
      <div className="ml-64 flex flex-col min-h-screen min-w-0" style={{overflowX: 'hidden'}}>
        <LayoutHeader title={pageTitles[currentPage] || 'Inicio'} onLogout={handleLogout} adminImage={adminImage} adminName={adminName} />
        <main className="flex-grow p-6 overflow-auto">
          {renderPage()}
        </main>
      </div>
    </div>
  );
};

export default App;

// DONE