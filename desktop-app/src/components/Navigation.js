import React, { useState } from 'react';
import './Navigation.css';

function Navigation({ currentPage, setCurrentPage }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const navItems = [
    { id: 'home', label: '🏠 Home' },
    { id: 'encrypt', label: '🔐 Encrypt' },
    { id: 'verify', label: '✓ Verify' }
  ];

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="logo">
          🛡️ Deepfake Defense
        </div>
        
        <ul className="nav-menu">
          {navItems.map(item => (
            <li key={item.id}>
              <button
                className={`nav-link ${currentPage === item.id ? 'active' : ''}`}
                onClick={() => setCurrentPage(item.id)}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}

export default Navigation;
