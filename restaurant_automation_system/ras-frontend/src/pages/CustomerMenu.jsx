import React, { useEffect, useMemo, useState } from 'react';
import { api } from '../services/api';
import './CustomerMenu.css';

const fallback = [
  { id: 'f1', name: 'Fire-Grilled Chicken', category: 'Chef favourites', description: 'Herb butter, charred lemon, garden greens.', price: '1450.00', image_url: 'https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=900&q=85' },
  { id: 'f2', name: 'Truffle Mushroom Pasta', category: 'Pasta', description: 'Wild mushrooms, parmesan, silky cream and herbs.', price: '1280.00', image_url: 'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=900&q=85' },
  { id: 'f3', name: 'Garden Burrata', category: 'Small plates', description: 'Tomatoes, basil oil, toasted sourdough and sea salt.', price: '980.00', image_url: 'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=85' },
];

function CustomerMenu() {
  const [items, setItems] = useState([]);
  const [active, setActive] = useState('All');
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [checkout, setCheckout] = useState(false);
  const [placing, setPlacing] = useState(false);
  const [confirmation, setConfirmation] = useState(null);
  const [form, setForm] = useState({ order_type: 'dine_in', table: '', customer_name: '', customer_phone: '', notes: '' });

  useEffect(() => {
    api.get('menu-items/').then(({ data }) => setItems(data.filter((item) => item.available))).catch(() => setItems(fallback)).finally(() => setLoading(false));
  }, []);

  const displayItems = items.length ? items : fallback;
  const categories = ['All', ...new Set(displayItems.map((item) => item.category || 'Mains'))];
  const filtered = active === 'All' ? displayItems : displayItems.filter((item) => (item.category || 'Mains') === active);
  const groupedCart = useMemo(() => Object.values(cart.reduce((acc, item) => {
    const key = item.id;
    acc[key] = acc[key] ? { ...acc[key], quantity: acc[key].quantity + 1 } : { ...item, quantity: 1 };
    return acc;
  }, {})), [cart]);
  const total = useMemo(() => cart.reduce((sum, item) => sum + Number(item.price), 0), [cart]);

  const removeOne = (id) => {
    const index = cart.findIndex((item) => item.id === id);
    if (index >= 0) setCart([...cart.slice(0, index), ...cart.slice(index + 1)]);
  };

  const placeOrder = async (event) => {
    event.preventDefault();
    if (groupedCart.some((item) => String(item.id).startsWith('f'))) {
      alert('Connect the backend and add real menu items before submitting a live order.');
      return;
    }
    setPlacing(true);
    try {
      const payload = {
        order_type: form.order_type,
        table: form.order_type === 'dine_in' && form.table ? Number(form.table) : null,
        customer_name: form.customer_name,
        customer_phone: form.customer_phone,
        notes: form.notes,
        order_details: groupedCart.map((item) => ({ menu_item: item.id, quantity: item.quantity, notes: '' })),
      };
      const { data } = await api.post('orders/', payload);
      setConfirmation(data);
      setCart([]);
      setCheckout(false);
    } catch (error) {
      alert(error.response?.data?.order_details || 'We could not place the order. Please ask a team member for help.');
    } finally {
      setPlacing(false);
    }
  };

  return (
    <div className="guest-shell">
      <nav className="guest-nav"><div className="brand"><span>S</span>Savour</div><div className="guest-links"><a href="#menu">Menu</a><a href="#story">Our story</a><button>Reserve a table</button></div></nav>
      <header className="food-hero"><div className="hero-copy"><span className="hero-kicker">Seasonal kitchen · warm hospitality</span><h1>Food worth<br/><em>slowing down</em> for.</h1><p>Thoughtful plates, bright ingredients and the kind of table you never want to leave.</p><a href="#menu" className="primary-cta">Explore the menu <i className="bi bi-arrow-down"/></a></div><div className="hero-image" role="img" aria-label="Beautifully plated restaurant meal"><span>Tonight's table is waiting.</span></div></header>
      <section className="menu-section" id="menu"><div className="section-heading"><div><span>Made to crave</span><h2>Choose your next favourite.</h2></div><p>Freshly prepared. Tell us what you love and what you need us to leave out.</p></div><div className="category-row">{categories.map((category) => <button className={active === category ? 'active' : ''} onClick={() => setActive(category)} key={category}>{category}</button>)}</div>{loading ? <div className="menu-loading">Preparing today's menu…</div> : <div className="dish-grid">{filtered.map((item) => <article className="dish-card" key={item.id}><div className="dish-image" style={{backgroundImage:`url("${item.image_url || fallback[0].image_url}")`}}><span>{item.category || 'Mains'}</span></div><div className="dish-copy"><div><h3>{item.name}</h3><p>{item.description || 'Prepared fresh to order with seasonal ingredients.'}</p></div><div className="dish-bottom"><strong>KSh {Number(item.price).toLocaleString()}</strong><button onClick={() => setCart([...cart, item])}><i className="bi bi-plus-lg"/></button></div></div></article>)}</div>}</section>
      <section className="story-band" id="story"><span>Our table</span><h2>Restaurant technology should disappear into the hospitality.</h2><p>The guest gets beauty and simplicity. Your team gets the order, kitchen and inventory data underneath it.</p></section>

      {cart.length > 0 && <div className="floating-order"><div><small>{cart.length} {cart.length === 1 ? 'item' : 'items'}</small><strong>KSh {total.toLocaleString()}</strong></div><button onClick={() => setCheckout(true)}>View order <i className="bi bi-arrow-right"/></button></div>}

      {checkout && <div className="checkout-backdrop" onClick={() => setCheckout(false)}><aside className="checkout-panel" onClick={(e) => e.stopPropagation()}><button className="checkout-close" onClick={() => setCheckout(false)}><i className="bi bi-x-lg"/></button><span className="hero-kicker">Your table</span><h2>Almost ready.</h2><div className="cart-lines">{groupedCart.map((item) => <div className="cart-line" key={item.id}><div><strong>{item.quantity} × {item.name}</strong><small>KSh {(Number(item.price) * item.quantity).toLocaleString()}</small></div><button onClick={() => removeOne(item.id)}>−</button></div>)}</div><div className="cart-total"><span>Total</span><strong>KSh {total.toLocaleString()}</strong></div><form onSubmit={placeOrder}><div className="order-type"><button type="button" className={form.order_type === 'dine_in' ? 'active' : ''} onClick={() => setForm({...form, order_type:'dine_in'})}>Dine in</button><button type="button" className={form.order_type === 'takeaway' ? 'active' : ''} onClick={() => setForm({...form, order_type:'takeaway', table:''})}>Takeaway</button></div>{form.order_type === 'dine_in' && <input placeholder="Table ID / scan from table QR" value={form.table} onChange={(e) => setForm({...form, table:e.target.value})} required/>}<input placeholder="Your name" value={form.customer_name} onChange={(e) => setForm({...form, customer_name:e.target.value})}/><input placeholder="Phone number" value={form.customer_phone} onChange={(e) => setForm({...form, customer_phone:e.target.value})}/><textarea placeholder="Anything we should know? Allergies, timing, special request…" value={form.notes} onChange={(e) => setForm({...form, notes:e.target.value})}/><button className="place-order" disabled={placing}>{placing ? 'Sending to kitchen…' : 'Place order'}</button></form></aside></div>}

      {confirmation && <div className="confirmation-toast"><i className="bi bi-check2-circle"/><div><strong>Order #{confirmation.id} is in.</strong><span>The kitchen has received it. We’ll take it from here.</span></div><button onClick={() => setConfirmation(null)}>×</button></div>}
    </div>
  );
}
export default CustomerMenu;
