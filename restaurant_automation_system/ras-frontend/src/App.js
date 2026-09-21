import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import MenuItemsPage from './pages/MenuItemsPage';
import AddMenuItem from './pages/AddMenuItem';
import OrdersPage from './pages/OrdersPage';
import CustomerMenu from './pages/CustomerMenu';

import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './App.css';

function App() {
  const location = useLocation();
  const customerExperience = location.pathname.startsWith('/menu');

  return (
    <div className="container-fluid p-0">
      {!customerExperience && (
        <>
          <header className="bg-dark text-white py-3 text-center shadow-sm">
            <h1 className="mb-0">Savour Restaurant OS</h1>
          </header>
          <nav className="navbar navbar-expand-md navbar-light bg-light px-3">
            <div className="container-fluid">
              <Link className="navbar-brand" to="/">
                <i className="bi bi-speedometer2 me-2"></i>Operations
              </Link>
              <div className="navbar-nav ms-auto">
                <Link className="nav-link" to="/menu-items">Menu Manager</Link>
                <Link className="nav-link" to="/orders">Orders</Link>
                <Link className="nav-link" to="/menu">Customer Menu</Link>
              </div>
            </div>
          </nav>
        </>
      )}

      <main className={customerExperience ? '' : 'px-4 py-3'}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/menu" element={<CustomerMenu />} />
          <Route path="/menu-items" element={<MenuItemsPage />} />
          <Route path="/add-menu-item" element={<AddMenuItem />} />
          <Route path="/orders" element={<OrdersPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
