import React from 'react';
import { Link } from 'react-router-dom';
import './Sidebar.css';

function Sidebar() {
  return (
    <div className="sidebar">
      <h2>Menu</h2>
      <ul>
        <li><Link to="/devices">Devices</Link></li>
        <li><Link to="/">Create Configuration</Link></li>
        <li><Link to="/info">Property information</Link></li>

      </ul>
    </div>
  );
}

export default Sidebar;
