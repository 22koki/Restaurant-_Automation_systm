import React from 'react';
import { Link } from 'react-router-dom';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './Sidebar.css';

const Sidebar = () => {
  const links = [
    { title: 'Dashboard', icon: 'bi-speedometer2', route: '/' },
    { title: 'Menu Items', icon: 'bi-list-ul', route: '/menu-items' },
    { title: 'Orders', icon: 'bi-cart-check', route: '/orders' },
    { title: 'Order Details', icon: 'bi-receipt', route: '/order-details' },
    { title: 'Ingredients', icon: 'bi-basket', route: '/ingredients' },
    { title: 'Inventory', icon: 'bi-boxes', route: '/inventory' },
    { title: 'Item Ingredients', icon: 'bi-diagram-3', route: '/item-ingredients' },
    { title: 'Purchase Orders', icon: 'bi-bag-plus', route: '/purchase-orders' },
    { title: 'Invoices', icon: 'bi-file-earmark-text', route: '/invoices' },
    { title: 'Cheques', icon: 'bi-currency-dollar', route: '/cheques' },
    { title: 'Low Stock Alerts', icon: 'bi-exclamation-triangle', route: '/low-stock' },
    { title: 'Menu Card', icon: 'bi-card-text', route: '/menu-card' },
    { title: 'Monthly Summary', icon: 'bi-calendar-event', route: '/monthly-summary' },
    { title: 'Print Cheques', icon: 'bi-printer', route: '/print-cheques' },
    { title: 'Reports', icon: 'bi-graph-up', route: '/reports' },
  ];

  return (
    <div className="sidebar d-flex flex-column p-3 bg-dark text-white">
      <h4 className="text-center mb-4">🍽️ RAS</h4>
      {links.map((link, index) => (
        <Link key={index} to={link.route} className="text-white nav-link my-2 d-flex align-items-center">
          <i className={`bi ${link.icon} me-2`}></i>
          {link.title}
        </Link>
      ))}
    </div>
  );
};

export default Sidebar;
