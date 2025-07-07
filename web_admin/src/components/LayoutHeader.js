import React from 'react';

const LayoutHeader = ({ title, onLogout, adminImage, adminName }) => {
  return (
    <header className="w-full bg-white px-8 py-4 flex justify-between items-center shadow-sm border-b border-gray-200 flex-shrink-0">
      <h1 className="text-2xl font-bold text-gray-800 tracking-tight">{title}</h1>
      <div className="flex items-center gap-4">
        <button
          onClick={onLogout}
          className="px-5 py-2 bg-red-500 text-white rounded-lg shadow hover:bg-red-600 transition-colors duration-200 font-semibold"
        >
          Cerrar Sesión
        </button>
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center shadow border border-blue-200 overflow-hidden">
            {adminImage ? (
              <img src={adminImage} alt="Admin" className="w-full h-full object-cover" />
            ) : (
              <span className="text-xl font-bold text-blue-700">
                {adminName ? adminName[0].toUpperCase() : <svg xmlns='http://www.w3.org/2000/svg' className='h-7 w-7' fill='none' viewBox='0 0 24 24' stroke='currentColor'><path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M5.121 17.804A13.937 13.937 0 0112 15c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0z' /></svg>}
              </span>
            )}
          </div>
          <span className="text-base font-medium text-gray-700 max-w-xs truncate">{adminName}</span>
        </div>
      </div>
    </header>
  );
};

export default LayoutHeader;