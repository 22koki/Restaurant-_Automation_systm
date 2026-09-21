// src/pages/MenuItems.jsx
import React, { useEffect, useState } from "react";
import "./MenuItems.css";
import { Link } from "react-router-dom";
import { api } from "../services/api";

const MenuItems = () => {
  const [items, setItems] = useState([]);

  const removeItem = async (item) => { if (!window.confirm(`Delete ${item.name}? This cannot be undone.`)) return; try { await api.delete(`menu-items/${item.id}/`); setItems(current => current.filter(x => x.id !== item.id)); } catch (error) { const detail=error.response?.data?.detail; alert(detail || 'This item could not be deleted. It may already be used by an order. You can edit it and mark it unavailable instead.'); } };

  useEffect(() => {
    // Fetch your menu items from the backend API
    api.get("menu-items/")

      .then((response) => {
        setItems(response.data);
      })
      .catch((error) => {
        console.error("Error fetching menu items:", error);
      });
  }, []);

  return (
    <div className="menu-items-page container">
      <h2 className="page-title">
        🍽️ Menu Items
      </h2>

      <div className="mb-3">
        <Link to="/add-menu-item" className="btn btn-primary">
          ➕ Add New Item
        </Link>
      </div>

      <div className="table-responsive">
        <table className="table table-striped table-hover custom-table">
          <thead className="table-dark">
            <tr>
              <th>#</th>
              <th>Name</th>
              <th>Description</th>
              <th>Price (Ksh)</th>
              <th>Category</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center">No items found.</td>
              </tr>
            ) : (
              items.map((item, index) => (
                <tr key={item.id}>
                  <td>{index + 1}</td>
                  <td>{item.name}</td>
                  <td>{item.description}</td>
                  <td>{item.price}</td>
                  <td>{item.category}</td>
                  <td>
                    <Link to={`/edit-menu-item/${item.id}`} className="btn btn-sm btn-warning me-2">
                      ✏️ Edit
                    </Link>
                    <button className="btn btn-sm btn-danger" onClick={() => removeItem(item)}>
                      🗑️ Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MenuItems;
