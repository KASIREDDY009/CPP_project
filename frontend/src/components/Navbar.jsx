import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navbar({ username, onLogout }) {
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? 'text-green-600 font-semibold' : 'text-gray-600 hover:text-green-600';

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/dashboard" className="text-xl font-bold text-green-600">
          SmartPantry
        </Link>
        <div className="flex items-center gap-6">
          <Link to="/dashboard" className={isActive('/dashboard')}>Dashboard</Link>
          <Link to="/pantry" className={isActive('/pantry')}>My Pantry</Link>
          <Link to="/add-item" className={isActive('/add-item')}>Add Item</Link>
          <span className="text-gray-400">|</span>
          <span className="text-sm text-gray-500">{username}</span>
          <button onClick={onLogout} className="text-sm text-red-500 hover:text-red-700">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
