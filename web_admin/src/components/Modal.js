import React from 'react';

const Modal = ({ children, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-gray-900 bg-opacity-40 backdrop-blur-sm" />
      <div className="relative bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg z-10 flex flex-col items-stretch">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-700 hover:text-blue-700 text-3xl font-extrabold bg-white bg-opacity-90 rounded-full border border-gray-300 shadow-lg w-10 h-10 flex items-center justify-center z-20 focus:outline-none"
          aria-label="Cerrar"
          style={{lineHeight: '1', padding: 0}}
        >
          &times;
        </button>
        {children}
      </div>
    </div>
  );
};

export default Modal;