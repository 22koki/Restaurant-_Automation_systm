import React, { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import './WaiterBoard.css';
import { useAuth } from '../context/AuthContext';

function WaiterBoard() {
  const [orders, setOrders] = useState([]);
  const { user } = useAuth();

  const load = useCallback(() => api.get('orders/').then(({ data }) => setOrders(data)), []);
  useEffect(() => { load(); const timer = setInterval(load, 15000); return () => clearInterval(timer); }, [load]);

  const myOrders = user?.role === 'waiter' ? orders.filter((order) => order.waiter === user.id) : orders;
  const readyOrders = myOrders.filter((order) => (order.details || []).some((item) => item.status === 'ready'));
  const serveItem = async (item, order) => {
    await api.patch(`order-details/${item.id}/`, { status: 'served' });
    const remaining = order.details.filter((detail) => detail.id !== item.id && !['served', 'cancelled'].includes(detail.status));
    if (!remaining.length) await api.patch(`orders/${order.id}/`, { status: 'served' });
    load();
  };

  return (
    <div className="waiter-shell">
      <header><span>Service pass</span><h1>Ready to run</h1><p>{user?.role === 'waiter' ? 'Only dishes assigned to you appear here. Run them while they are hot.' : 'Food the kitchen has marked ready appears here immediately.'}</p></header>
      <div className="ready-grid">
        {readyOrders.map((order) => (
          <article className="ready-order" key={order.id}>
            <div className="ready-order-head"><strong>{order.table ? `Table ${order.table_number || order.table}` : order.order_type.replace('_', ' ')}</strong><span>Order #{order.id}</span></div>
            {(order.details || []).filter((item) => item.status === 'ready').map((item) => (
              <div className="ready-item" key={item.id}><div><h3>{item.quantity} × {item.menu_item_name}</h3>{item.notes && <p>{item.notes}</p>}</div><button onClick={() => serveItem(item, order)}>Served</button></div>
            ))}
          </article>
        ))}
        {!readyOrders.length && <div className="all-clear"><i className="bi bi-check2-circle"/><h2>Pass is clear</h2><p>No dishes are waiting to be served.</p></div>}
      </div>
    </div>
  );
}
export default WaiterBoard;
