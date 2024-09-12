import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './DeviceListView.css';

const DeviceListView = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState('');

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/devices/');
        setDevices(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDevices();
  }, []);

  const handleFilterChange = (e) => {
    setFilterType(e.target.value);
  };

  const filteredAndSortedDevices = devices
    .filter(device => (filterType ? device.type === filterType : true))
    .sort((a, b) => a.type.localeCompare(b.type));

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error loading devices: {error.message}</p>;

  return (
    <div className="device-list-view">
      <h2>Devices List</h2>

      <div className="filter-container">
        <label htmlFor="device-type-filter">Filter by Type:</label>
        <select id="device-type-filter" value={filterType} onChange={handleFilterChange}>
          <option value="">All</option>
          {Array.from(new Set(devices.map(device => device.type))).map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      <div className="device-cards">
        {filteredAndSortedDevices.map((device) => (
          <div key={device.id} className="device-card">
            <h3>{device.model}</h3>
            <div className="device-field">
              <strong>Type:</strong>
              <span>{device.type}</span>
            </div>
            <div className="device-field">
              <strong>Capability:</strong>
              <span>{device.capability}</span>
            </div>
            {device.impact !== null && (
              <div className="device-field">
                <strong>Impact:</strong>
                <span>{device.impact}</span>
              </div>
            )}
            {device.risk !== null && (
              <div className="device-field">
                <strong>Risk:</strong>
                <span>{device.risk}</span>
              </div>
            )}
            {device.sustainability !== null && (
              <div className="device-field">
                <strong>Sustainability:</strong>
                <span>{device.sustainability}</span>
              </div>
            )}
            <div className="device-field">
              <strong>Connectivities:</strong>
              <span>{device.connectivities.map(c => c.technology).join(', ') || 'None'}</span>
            </div>
            <div className="device-field">
              <strong>Power Supplies:</strong>
              <span>{device.power_supplies.map(p => p.source).join(', ') || 'None'}</span>
            </div>
            <div className="device-field">
              <strong>Apps:</strong>
              <span>{device.apps.map(a => a.name).join(', ') || 'Not required'}</span>
            </div>
            <div className="device-field">
              <strong>Vulnerabilities:</strong>
              <span>{device.vulnerabilities.map(v => v.identifier).join(', ') || 'None'}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DeviceListView;
