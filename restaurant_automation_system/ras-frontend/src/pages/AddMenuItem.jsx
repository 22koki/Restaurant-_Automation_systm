// src/pages/AddMenuItem.jsx
import React, { useState } from "react";
import "./AddMenuItem.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const AddMenuItem = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    price: "",
    available: true  // Add default value
  });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!formData.name || !formData.price) {
      setError("Please fill in all required fields.");
      return;
    }

    axios.post("http://localhost:8000/api/menu-items/", formData)
      .then(() => navigate("/menu-items"))
      .catch((error) => {
        console.error("Error adding menu item:", error);
        setError("An error occurred while saving. Please try again.");
      });
  };

  return (
    <div className="add-menu-item container">
      <h2 className="page-title">➕ Add New Menu Item</h2>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSubmit} className="form-container">
        <div className="mb-3">
          <label className="form-label">Name *</label>
          <input
            type="text"
            className="form-control"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="e.g., Grilled Chicken"
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">Price (Ksh) *</label>
          <input
            type="number"
            className="form-control"
            name="price"
            value={formData.price}
            onChange={handleChange}
            placeholder="e.g., 450"
            required
          />
        </div>

        <div className="mb-3 form-check">
          <input
            type="checkbox"
            className="form-check-input"
            name="available"
            checked={formData.available}
            onChange={handleChange}
          />
          <label className="form-check-label">Available</label>
        </div>

        <button type="submit" className="btn btn-success">
          ✅ Save Item
        </button>
        <button
          type="button"
          className="btn btn-secondary ms-2"
          onClick={() => navigate("/menu-items")}
        >
          ⬅️ Cancel
        </button>
      </form>
    </div>
  );
};

export default AddMenuItem;
