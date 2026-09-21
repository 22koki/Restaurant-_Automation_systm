import React from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

const modules = [
  { to: '/orders', icon: 'bi-receipt-cutoff', title: 'Live Orders', text: 'Follow every ticket from confirmation to service.' },
  { to: '/menu-items', icon: 'bi-journal-richtext', title: 'Menu Studio', text: 'Manage dishes, pricing, availability and prep stations.' },
  { to: '/menu', icon: 'bi-phone', title: 'Guest Experience', text: 'Preview the mobile-first menu your customers will use.' },
  { to: '/inventory', icon: 'bi-box-seam', title: 'Inventory', text: 'Track ingredients, usage and low-stock risk.' },
  { to: '/tables', icon: 'bi-grid-3x3-gap', title: 'Tables', text: 'See availability, occupied tables and service state.' },
  { to: '/reservations', icon: 'bi-calendar2-check', title: 'Reservations', text: 'Manage upcoming guests, party sizes and seating.' },
];

function Dashboard() {
  return (
    <div className="ops-shell">
      <section className="ops-hero">
        <div>
          <span className="eyebrow">Restaurant command centre</span>
          <h1>Good service starts with a calm, clear view.</h1>
          <p>Orders, tables, kitchen flow, inventory and guests — connected in one operating system.</p>
        </div>
        <Link to="/menu" className="guest-preview">Open guest menu <i className="bi bi-arrow-up-right" /></Link>
      </section>

      <section className="ops-status">
        <div><span>Open orders</span><strong>—</strong><small>Live API data next</small></div>
        <div><span>Tables in service</span><strong>—</strong><small>Floor view ready for wiring</small></div>
        <div><span>Kitchen queue</span><strong>—</strong><small>Ticket workflow prepared</small></div>
        <div><span>Low stock</span><strong>—</strong><small>Inventory alerts available</small></div>
      </section>

      <section className="ops-modules">
        {modules.map((module) => (
          <Link to={module.to} className="ops-module" key={module.title}>
            <i className={`bi ${module.icon}`} />
            <div><h3>{module.title}</h3><p>{module.text}</p></div>
            <i className="bi bi-arrow-right arrow" />
          </Link>
        ))}
      </section>
    </div>
  );
}

export default Dashboard;
