import React, { useEffect, useState } from "react";
import "./MenuItems.css";
import { Link } from "react-router-dom";
import { api } from "../services/api";

const money = value => Number(value || 0).toLocaleString("en-KE", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export default function MenuItems() {
  const [items, setItems] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [recipeForm, setRecipeForm] = useState({ menu_item: "", ingredient: "", quantity_required: "" });
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const [menu, ing, recipe] = await Promise.all([
        api.get("menu-items/"),
        api.get("ingredients/"),
        api.get("item-ingredients/")
      ]);
      setItems(menu.data);
      setIngredients(ing.data);
      setRecipes(recipe.data);
    } catch (e) {
      setError("Could not load menu costing data.");
    }
  };

  useEffect(() => { load(); }, []);

  const removeItem = async item => {
    if (!window.confirm(`Delete ${item.name}? This cannot be undone.`)) return;
    try {
      await api.delete(`menu-items/${item.id}/`);
      setItems(current => current.filter(x => x.id !== item.id));
    } catch (e) {
      alert(e.response?.data?.detail || "This item could not be deleted. Mark it unavailable instead.");
    }
  };

  const addRecipeLine = async e => {
    e.preventDefault();
    setError("");
    try {
      await api.post("item-ingredients/", {
        menu_item: Number(recipeForm.menu_item),
        ingredient: Number(recipeForm.ingredient),
        quantity_required: Number(recipeForm.quantity_required)
      });
      setRecipeForm({ ...recipeForm, ingredient: "", quantity_required: "" });
      await load();
    } catch (e) {
      setError(JSON.stringify(e.response?.data || "Could not add ingredient to recipe."));
    }
  };

  const removeRecipeLine = async id => {
    try {
      await api.delete(`item-ingredients/${id}/`);
      await load();
    } catch (e) {
      setError("Could not remove recipe ingredient.");
    }
  };

  const selected = items.find(x => String(x.id) === String(recipeForm.menu_item));

  return (
    <main className="menu-items-page container">
      <div className="menu-title-row">
        <div><span className="eyebrow">Menu intelligence</span><h2 className="page-title">Dish profitability</h2><p>Build recipes and see exactly what each plate costs and earns.</p></div>
        <Link to="/add-menu-item" className="btn btn-primary">+ Add New Item</Link>
      </div>
      {error && <div className="alert alert-danger">{error}</div>}

      <section className="costing-grid">
        {items.map(item => {
          const pct = Number(item.food_cost_percentage || 0);
          return <article className="cost-card" key={item.id}>
            <div className="cost-card-top"><div><small>{item.category}</small><h3>{item.name}</h3></div><span className={pct > 35 ? "cost-badge high" : "cost-badge"}>{pct.toFixed(1)}% food cost</span></div>
            <div className="cost-numbers"><div><small>Selling price</small><strong>KSh {money(item.price)}</strong></div><div><small>Food cost</small><strong>KSh {money(item.food_cost)}</strong></div><div><small>Gross profit</small><strong>KSh {money(item.gross_profit)}</strong></div><div><small>Margin</small><strong>{Number(item.gross_margin_percentage || 0).toFixed(1)}%</strong></div></div>
            <div className="recipe-lines">
              {(item.recipe || []).length ? item.recipe.map(line => <div key={line.id}><span>{line.ingredient_name} · {line.quantity_required} {line.unit}</span><b>KSh {money(line.line_cost)}</b></div>) : <em>No recipe ingredients yet.</em>}
            </div>
            <div className="cost-actions"><Link to={`/edit-menu-item/${item.id}`} className="btn btn-sm btn-warning">Edit dish</Link><button className="btn btn-sm btn-danger" onClick={() => removeItem(item)}>Delete</button></div>
          </article>;
        })}
      </section>

      <section className="recipe-builder">
        <div><span className="eyebrow">Recipe builder</span><h3>Add ingredient to a dish</h3><p>Quantity is the amount used for one serving. Ingredient unit cost comes from Inventory.</p></div>
        <form onSubmit={addRecipeLine}>
          <label>Dish<select required value={recipeForm.menu_item} onChange={e => setRecipeForm({...recipeForm,menu_item:e.target.value})}><option value="">Choose dish</option>{items.map(x=><option key={x.id} value={x.id}>{x.name}</option>)}</select></label>
          <label>Ingredient<select required value={recipeForm.ingredient} onChange={e => setRecipeForm({...recipeForm,ingredient:e.target.value})}><option value="">Choose ingredient</option>{ingredients.map(x=><option key={x.id} value={x.id}>{x.name} ({x.unit}) · KSh {money(x.cost_per_unit)}</option>)}</select></label>
          <label>Qty / serving<input required type="number" min="0.0001" step="0.0001" value={recipeForm.quantity_required} onChange={e => setRecipeForm({...recipeForm,quantity_required:e.target.value})}/></label>
          <button type="submit">Add to recipe</button>
        </form>
        {selected && <div className="selected-recipe"><h4>{selected.name} recipe</h4>{recipes.filter(r=>r.menu_item===selected.id).map(r=>{const ing=ingredients.find(i=>i.id===r.ingredient);return <div key={r.id}><span>{ing?.name || "Ingredient"} · {r.quantity_required} {ing?.unit || ""}</span><button onClick={()=>removeRecipeLine(r.id)}>Remove</button></div>})}</div>}
      </section>
    </main>
  );
}
