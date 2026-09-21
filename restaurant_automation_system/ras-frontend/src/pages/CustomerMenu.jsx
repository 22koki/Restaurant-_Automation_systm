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

  useEffect(() => {
    api.get('menu-items/')
      .then(({ data }) => setItems(data.filter((item) => item.available)))
      .catch(() => setItems(fallback))
      .finally(() => setLoading(false));
  }, []);

  const displayItems = items.length ? items : fallback;
  const categories = ['All', ...new Set(displayItems.map((item) => item.category || 'Mains'))];
  const filtered = active === 'All' ? displayItems : displayItems.filter((item) => (item.category || 'Mains') === active);
  const total = useMemo(() => cart.reduce((sum, item) => sum + Number(item.price), 0), [cart]);

  return (
    <div className="guest-shell">
      <nav className="guest-nav">
        <div className="brand"><span>S</span>Savour</div>
        <div className="guest-links"><a href="#menu">Menu</a><a href="#story">Our story</a><button>Reserve a table</button></div>
      </nav>

      <header className="food-hero">
        <div className="hero-copy">
          <span className="hero-kicker">Seasonal kitchen · warm hospitality</span>
          <h1>Food worth<br/><em>slowing down</em> for.</h1>
          <p>Thoughtful plates, bright ingredients and the kind of table you never want to leave.</p>
          <a href="#menu" className="primary-cta">Explore the menu <i className="bi bi-arrow-down"/></a>
        </div>
        <div className="hero-image" role="img" aria-label="Beautifully plated restaurant meal"><span>Tonight's table is waiting.</span></div>
      </header>

      <section className="menu-section" id="menu">
        <div className="section-heading"><div><span>Made to crave</span><h2>Choose your next favourite.</h2></div><p>Freshly prepared. Tell us what you love and what you need us to leave out.</p></div>
        <div className="category-row">{categories.map((category) => <button className={active === category ? 'active' : ''} onClick={() => setActive(category)} key={category}>{category}</button>)}</div>
        {loading ? <div className="menu-loading">Preparing today's menu…</div> : (
          <div className="dish-grid">
            {filtered.map((item) => (
              <article className="dish-card" key={item.id}>
                <div className="dish-image" style={{backgroundImage:`url("${item.image_url || fallback[0].image_url}")`}}><span>{item.category || 'Mains'}</span></div>
                <div className="dish-copy"><div><h3>{item.name}</h3><p>{item.description || 'Prepared fresh to order with seasonal ingredients.'}</p></div><div className="dish-bottom"><strong>KSh {Number(item.price).toLocaleString()}</strong><button onClick={() => setCart([...cart, item])} aria-label={`Add ${item.name} to order`}><i className="bi bi-plus-lg"/></button></div></div>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="story-band" id="story"><span>Our table</span><h2>Restaurant technology should disappear into the hospitality.</h2><p>The guest gets beauty and simplicity. Your team gets the order, kitchen and inventory data underneath it.</p></section>

      {cart.length > 0 && <div className="floating-order"><div><small>{cart.length} {cart.length === 1 ? 'item' : 'items'}</small><strong>KSh {total.toLocaleString()}</strong></div><button>View order <i className="bi bi-arrow-right"/></button></div>}
    </div>
  );
}

export default CustomerMenu;
