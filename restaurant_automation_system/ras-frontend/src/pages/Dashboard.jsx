// src/pages/Dashboard.jsx
import React from 'react';
import { Link } from 'react-router-dom';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './Dashboard.css'; // Custom styles

function Dashboard() {
  return (
    <div className="dashboard-container">
      <header className="text-center mb-5">
        <h1 className="dashboard-title">
          🍽️ Welcome to <span className="highlight">RestoPro</span> Dashboard
        </h1>
        <p className="lead">Your central hub for managing orders, inventory, and reports</p>
      </header>

      <div className="row g-4 justify-content-center">

        <Link to="/menu-items" className="col-md-4 text-decoration-none">
          <div className="card dashboard-card shadow-sm">
            <div className="card-body text-center">
              <i className="bi bi-card-list icon-large"></i>
              <h5 className="card-title mt-3">Menu Items</h5>
              <p className="card-text">Manage and update all your restaurant menu items.</p>
            </div>
          </div>
        </Link>

        <Link to="/orders" className="col-md-4 text-decoration-none">
          <div className="card dashboard-card shadow-sm">
            <div className="card-body text-center">
              <i className="bi bi-receipt-cutoff icon-large"></i>
              <h5 className="card-title mt-3">Orders</h5>
              <p className="card-text">Track current and historical customer orders.</p>
            </div>
          </div>
        </Link>

        <Link to="/inventory" className="col-md-4 text-decoration-none">
          <div className="card dashboard-card shadow-sm">
            <div className="card-body text-center">
              <i className="bi bi-box-seam icon-large"></i>
              <h5 className="card-title mt-3">Inventory</h5>
              <p className="card-text">View and manage ingredient stocks.</p>
            </div>
          </div>
        </Link>

        <Link to="/reports" className="col-md-4 text-decoration-none">
          <div className="card dashboard-card shadow-sm">
            <div className="card-body text-center">
              <i className="bi bi-bar-chart-line icon-large"></i>
              <h5 className="card-title mt-3">Reports</h5>
              <p className="card-text">Access detailed reports and sales summaries.</p>
            </div>
          </div>
        </Link>

        <Link to="/cheques" className="col-md-4 text-decoration-none">
          <div className="card dashboard-card shadow-sm">
            <div className="card-body text-center">
              <i className="bi bi-printer icon-large"></i>
              <h5 className="card-title mt-3">Cheque Printing</h5>
              <p className="card-text">Print payment cheques for your records.</p>
            </div>
          </div>
        </Link>

      </div>
    </div>
  );
}

export default Dashboard;
