import React from 'react';
import { FaUtensils, FaShoppingCart, FaList, FaBoxes } from 'react-icons/fa';
import { motion } from 'framer-motion';
import './Dashboard.css'; // optional custom styles

const Dashboard = () => {
  return (
    <div className="container-fluid p-4 bg-dark text-white" style={{ minHeight: '100vh' }}>
      <motion.h1 
        className="text-center mb-4 display-4 fw-bold"
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 1 }}
      >
        🍽️ Restaurant Automation Dashboard
      </motion.h1>

      <div className="row g-4">
        <motion.div 
          className="col-md-6 col-lg-3"
          whileHover={{ scale: 1.05 }}
        >
          <div className="card bg-secondary text-white h-100 shadow-lg">
            <div className="card-body text-center">
              <FaUtensils size={40} />
              <h5 className="card-title mt-2">Menu Items</h5>
              <p className="card-text">View and manage available dishes.</p>
            </div>
          </div>
        </motion.div>

        <motion.div 
          className="col-md-6 col-lg-3"
          whileHover={{ scale: 1.05 }}
        >
          <div className="card bg-info text-white h-100 shadow-lg">
            <div className="card-body text-center">
              <FaShoppingCart size={40} />
              <h5 className="card-title mt-2">Orders</h5>
              <p className="card-text">Track customer orders in real-time.</p>
            </div>
          </div>
        </motion.div>

        <motion.div 
          className="col-md-6 col-lg-3"
          whileHover={{ scale: 1.05 }}
        >
          <div className="card bg-success text-white h-100 shadow-lg">
            <div className="card-body text-center">
              <FaList size={40} />
              <h5 className="card-title mt-2">Inventory</h5>
              <p className="card-text">Monitor and reorder ingredients.</p>
            </div>
          </div>
        </motion.div>

        <motion.div 
          className="col-md-6 col-lg-3"
          whileHover={{ scale: 1.05 }}
        >
          <div className="card bg-warning text-dark h-100 shadow-lg">
            <div className="card-body text-center">
              <FaBoxes size={40} />
              <h5 className="card-title mt-2">Stock Alerts</h5>
              <p className="card-text">Check low-stock inventory levels.</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
