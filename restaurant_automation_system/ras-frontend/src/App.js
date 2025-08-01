// App.js
import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import MenuItemsPage from './pages/MenuItemsPage';

function App() {
  return (
    <div className="container mt-3">
      <h1 className="text-center mb-4">🍽️ Restaurant Automation System</h1>

      {/* Navigation Links */}
      <nav className="nav justify-content-center mb-4">
        <Link className="nav-link" to="/">Dashboard</Link>
        <Link className="nav-link" to="/menu-items">Menu Items</Link>
      </nav>

      {/* Page Routes */}
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/menu-items" element={<MenuItemsPage />} />
      </Routes>
    </div>
  );
}

export default App;
