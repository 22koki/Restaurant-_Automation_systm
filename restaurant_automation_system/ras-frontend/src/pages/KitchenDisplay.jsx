import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '../services/api';
import './KitchenDisplay.css';

const columns = [
  { key: 'queued', title: 'New tickets', icon: 'bi-bell' },
  { key: 'preparing', title: 'Preparing', icon: 'bi-fire' },
  { key: 'ready', title: 'Ready for service', icon: 'bi-check2-circle' },
];

function KitchenDisplay() {
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState('');

  const loadOrders = useCallback(() => {
    api.get('orders/')
      .then(({ data }) => { setOrders(data); setError(''); })
      .catch(() => setError('Kitchen feed is unavailable. Check the backend connection.'));
  }, []);

  useEffect(() => {
    loadOrders();
    const timer = setInterval(loadOrders, 15000);
    return () => clearInterval(timer);
  }, [loadOrders]);

  const tickets = useMemo(() => orders.flatMap((order) =>
    (order.details || [])
      .filter((item) => item.status !== 'served' && item.status !== 'cancelled')
      .map((item) => ({ ...item, orderId: order.id, table: order.table, orderType: order.order_type, createdAt: order.created_at }))
  ), [orders]);

  const updateItem = async (item, status) => {
    await api.patch(`order-details/${item.id}/`, { status });
    if (status === 'preparing') await api.patch(`orders/${item.orderId}/`, { status: 'preparing' });
    loadOrders();
  };

  return (
    <div className="kds-shell">
      <header className="kds-header">
        <div><span>Live kitchen</span><h1>Kitchen display</h1></div>
        <div className="kds-live"><i className="bi bi-circle-fill"/> Live · refreshes every 15s</div>
      </header>
      {error && <div className="kds-error">{error}</div>}
      <div className="kds-board">
        {columns.map((column) => (
          <section className="kds-column" key={column.key}>
            <div className="kds-column-title"><div><i className={`bi ${column.icon}`}/><strong>{column.title}</strong></div><span>{tickets.filter((ticket) => ticket.status === column.key).length}</span></div>
            <div className="kds-list">
              {tickets.filter((ticket) => ticket.status === column.key).map((ticket) => (
                <article className="ticket" key={ticket.id}>
                  <div className="ticket-top"><strong>#{ticket.orderId}</strong><span>{ticket.table ? `Table ${ticket.table}` : ticket.orderType.replace('_', ' ')}</span></div>
                  <h3>{ticket.quantity} × {ticket.menu_item_name}</h3>
                  <p className="station">{ticket.prep_station}</p>
                  {ticket.notes && <p className="ticket-note">“{ticket.notes}”</p>}
                  <small>{new Date(ticket.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</small>
                  {column.key === 'queued' && <button onClick={() => updateItem(ticket, 'preparing')}>Start preparing</button>}
                  {column.key === 'preparing' && <button onClick={() => updateItem(ticket, 'ready')}>Mark ready</button>}
                  {column.key === 'ready' && <button className="secondary" onClick={() => updateItem(ticket, 'served')}>Mark served</button>}
                </article>
              ))}
              {!tickets.some((ticket) => ticket.status === column.key) && <div className="empty-column">Nothing here right now.</div>}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}

export default KitchenDisplay;
