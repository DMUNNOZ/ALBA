import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import './ResponseView.css';

const ResponseView = () => {
  const location = useLocation();
  const data = location.state?.data;

  if (!data) return <p>No data available.</p>;

  const { properties, devices } = data;
  const [filterType, setFilterType] = useState('');

  const handleFilterChange = (e) => {
    setFilterType(e.target.value);
  };

  const filteredAndSortedDevices = devices
    .filter(device => (filterType ? device.type === filterType : true))
    .sort((a, b) => a.type.localeCompare(b.type));

  return (
    <div className="response-view">
      <h2>Properties</h2>
      <div className="properties">
        {properties.security && (
          <div className="property-item security">
            <strong>Average Impact: </strong>
            <span>{properties.security.average_impact}</span>
            <span className="info-icon">i
              <div className="custom-tooltip">
              Average impact of the resulting configuration, calculated from the individual impact values of the selected devices.
              </div>
            </span>          
          </div>
        )}
        {properties.security && properties.security.cwe_set && (
          <div className="property-item cwe-set">
            <strong>CWE Set: </strong>
            <span>{properties.security.cwe_set.join(', ') || 'Empty'}</span>
            <span className="info-icon">i
              <div className="custom-tooltip">
              List of CWE linked to the resulting configuration.
              </div>
            </span>          
          </div>
        )}
        {properties.usability && (
          <div className="property-item usability">
            <strong>Usability: </strong>
            <span>{properties.usability.join(', ') || 'Not required'}</span>
            <span className="info-icon">i
              <div className="custom-tooltip">
              List of applications required for managing the devices that belong to the generated configuration.
              <br />
              <br />Poor - More than 3 apps
              <br />Good - Between 1 and 3 apps
              <br />Excellent - No app required
              </div>
            </span>          
          </div>
        )}
        {properties.connectivity && (
          <div className="property-item connectivity">
            <strong>Connectivity: </strong>
            <span>{properties.connectivity.join(', ') || 'None'}</span>
            <span className="info-icon">i
              <div className="custom-tooltip">
              List of connectivity technologies present in the resulting configuration.
              <br />
              <br />Low - Less than 3 different connectivity technologies
              <br />Medium - Between 3 and 5 different connectivity technologies
              <br />High - More than 5 different connectivity technologies
              </div>
            </span>            
          </div>
        )}
        {properties.average_sustainability !== undefined && (
          <div className="property-item sustainability">
            <strong>Average Sustainability: </strong>
            <span>{properties.average_sustainability}</span>
            <span className="info-icon">i
              <div className="custom-tooltip">
              Average sustainability of the resulting configuration, calculated from the individual sustainability values of the selected devices.
              <br />
              <br />Low - Less than 4
              <br />Medium - Between 4 and 8
              <br />High - More than 8
              </div>
            </span>          
          </div>
        )}
      </div>
      <h3></h3>

      <h2>Devices</h2>
      
      <div className="filter-container">
        <label htmlFor="device-type-filter">Filter by Type:</label>
        <select id="device-type-filter" value={filterType} onChange={handleFilterChange}>
          <option value="">All</option>
          {Array.from(new Set(devices.map(device => device.type))).map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      <div className="devices">
        {filteredAndSortedDevices.map((device, index) => (
          <div key={index} className="device">
            <h3>{device.model}</h3> 
            <div className="device-field type">
              <strong>Type:</strong>
              <span>{device.type}</span>
            </div>
            {device.security && (
              <div className="device-field security-impact">
                <strong>Security Impact:</strong>
                <span>{device.security.impact}</span>
              </div>
            )}
            {device.security && device.security.cwe_set && (
              <div className="device-field cwe-set">
                <strong>CWE Set:</strong>
                <span>{device.security.cwe_set.join(', ') || 'Empty'}</span>
              </div>
            )}
            {device.usability && (
              <div className="device-field usability">
                <strong>Usability:</strong>
                <span>{device.usability.join(', ') || 'Not required'}</span>
              </div>
            )}
            {device.connectivity && (
              <div className="device-field connectivity">
                <strong>Connectivity:</strong>
                <span>{device.connectivity.join(', ') || 'None'}</span>
              </div>
            )}
            {device.sustainability !== undefined && (
              <div className="device-field sustainability">
                <strong>Sustainability:</strong>
                <span>{device.sustainability}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResponseView;
