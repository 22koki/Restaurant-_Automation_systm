// src/pages/OrdersPage.jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './OrdersPage.css';

const OrdersPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/orders/')
      .then(res => {
        setOrders(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching orders:", err);
        setError("Failed to load orders.");
        setLoading(false);
      });
  }, []);

  return (
    <div
      className="container-fluid min-vh-100 p-4"
      style={{
        backgroundImage: `url("/images/istockphoto-1150377750-2048x2048.jpg")`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
        color: '#fff'
      }}
    >
      <h2 className="mb-4 text-center text-white">Orders</h2>

      {loading && <p>Loading orders...</p>}
      {error && <p className="text-danger">{error}</p>}

      {!loading && !error && orders.length === 0 && (
        <p>No orders found.</p>
      )}

      {!loading && !error && orders.length > 0 && (
        <div className="row">
          {orders.map(order => (
            <div className="col-md-6 mb-4" key={order.id}>
              <div className="card text-dark shadow-sm">
                <div className="card-body">
                  <h5 className="card-title">Order #{order.id}</h5>
                  <p><strong>Sales Clerk:</strong> {order.salesclerk_username || 'N/A'}</p>
                  <p><strong>Date:</strong> {new Date(order.created_at).toLocaleString()}</p>
                  <p><strong>Total:</strong> KES {order.total}</p>

                  {order.details && order.details.length > 0 && (
                    <>
                      <h6>Items:</h6>
                      <ul className="list-group">
                        {order.details.map((item, index) => (
                          <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                            {item.quantity} x {item.menu_item_name}
                            <span>KES {item.subtotal}</span>
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default OrdersPage;
