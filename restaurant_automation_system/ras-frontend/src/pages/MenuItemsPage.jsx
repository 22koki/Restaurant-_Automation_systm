import React, { useEffect, useState } from 'react';
import { api } from '../services/api';

function MenuItemsPage() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    api.get('menu-items/')
      .then(res => setItems(res.data))
      .catch(err => console.error('Error fetching menu items:', err));
  }, []);

  return (
    <div>
      <h2>Menu Items</h2>
      <ul>
        {items.map(item => (
          <li key={item.id}>{item.name} - KES {item.price}</li>
        ))}
      </ul>
    </div>
  );
}

export default MenuItemsPage;
