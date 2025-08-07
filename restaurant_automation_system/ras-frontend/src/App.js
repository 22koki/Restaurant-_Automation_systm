// src/App.js
import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import MenuItemsPage from './pages/MenuItemsPage';
import AddMenuItem from "./pages/AddMenuItem";
import OrdersPage from './pages/OrdersPage';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './App.css'; // Optional if you have global styles

function App() {
  return (
    <div className="container-fluid p-0">
      {/* Header */}
      <header className="bg-dark text-white py-3 text-center shadow-sm">
        <h1 className="mb-0">🍽️ Restaurant Automation System</h1>
      </header>

      {/* Navigation */}
      <nav className="navbar navbar-expand-md navbar-light bg-light px-3">
        <div className="container-fluid">
          <Link className="navbar-brand" to="/">
            <i className="bi bi-speedometer2 me-2"></i>Dashboard
          </Link>
          <div className="collapse navbar-collapse">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item">
                <Link className="nav-link" to="/menu-items">
                  <i className="bi bi-card-list me-1"></i>Menu Items
                </Link>
              </li>
              {/* Add more nav items as needed */}
            </ul>
          </div>
        </div>
      </nav>

      {/* Routes */}
      <main className="px-4 py-3">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/menu-items" element={<MenuItemsPage />} />
          <Route path="/add-menu-item" element={<AddMenuItem />} />
          <Route path="/orders" element={<OrdersPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
