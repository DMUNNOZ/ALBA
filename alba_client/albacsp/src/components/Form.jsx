import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Form.css';

const newConfigDeviceLabels = {
  switch: 'Nº Switches:',
  router: 'Nº Routers:',
  bridge: 'Nº Bridges:',
  repeater: 'Nº Repeaters:',
  modern: 'Nº Modems:',
  gateway: 'Nº Gateways:',
  firewall: 'Nº Firewalls:',
  low_end_sensor: 'Nº Low-End Sensors:',
  high_end_sensor: 'Nº High-End Sensors:',
  bulb: 'Nº Bulbs:',
  energy_management: 'Nº Energy Management Devices:',
  lock: 'Nº Locks:',
  security_alarm: 'Nº Security Alarms:',
  security_ip_camera: 'Nº Security IP Cameras:',
  appliance: 'Nº Smart Appliances:',
  tv: 'Nº Smart TVs:',
  smartphone: 'Nº Smartphones:',
  tablet: 'Nº Tablets:',
  pc: 'Nº PCs:',
  smartwatch: 'Nº Smartwatches:',
  security_hub: 'Nº Security Hubs:',
  assistant_hub: 'Nº Assistant Hubs:',
  nas: 'Nº NAS Devices:',
};

const availableDeviceLabels = {
  switch: 'Switches:',
  router: 'Routers:',
  bridge: 'Bridges:',
  repeater: 'Repeaters:',
  modern: 'Modems:',
  gateway: 'Gateways:',
  firewall: 'Firewalls:',
  low_end_sensor: 'Low-End Sensors:',
  high_end_sensor: 'High-End Sensors:',
  bulb: 'Bulbs:',
  energy_management: 'Energy Management Devices:',
  lock: 'Locks:',
  security_alarm: 'Security Alarms:',
  security_ip_camera: 'Security IP Cameras:',
  appliance: ' Smart Appliances:',
  tv: 'Smart TVs:',
  smartphone: 'Smartphones:',
  tablet: 'Tablets:',
  pc: 'PCs:',
  smartwatch: 'Smartwatches:',
  security_hub: 'Security Hubs:',
  assistant_hub: 'Assistant Hubs:',
  nas: 'NAS Devices:',
};

const Form = () => {
  const initialState = {
    newConfigDevices: {
      switch: 0,
      router: 0,
      bridge: 0,
      repeater: 0,
      modern: 0,
      gateway: 0,
      firewall: 0,
      low_end_sensor: 0,  
      high_end_sensor: 0, 
      bulb: 0,
      energy_management: 0, 
      lock: 0,
      security_alarm: 0, 
      security_ip_camera: 0, 
      appliance: 0,
      tv: 0,
      smartphone: 0,
      tablet: 0,
      pc: 0, 
      smartwatch: 0,
      security_hub: 0, 
      assistant_hub: 0,
      nas: 0,
    },
    availableDevices: {
      switch: '',
      router: '',
      bridge: '',
      repeater: '',
      modern: '',
      gateway: '',
      firewall: '',
      low_end_sensor: '',
      high_end_sensor: '',
      bulb: '',
      energy_management: '',
      lock: '',
      security_alarm: '',
      security_ip_camera: '',
      appliance: '',
      tv: '',
      smartphone: '',
      tablet: '',
      pc: '',
      smartwatch: '',
      security_hub: '',
      assistant_hub: '',
      nas: '',
    },
    properties: {
      security: 'NONE',
      usability: 'NONE',
      connectivity: 'NONE',
      sustainability: 'NONE',
    },
  };

  const [formData, setFormData] = useState(initialState);
  const [jsonResult, setJsonResult] = useState(JSON.stringify(initialState, null, 2));
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    const [section, key] = name.split('.');

    let newValue;
    if (section === 'availableDevices') {
      newValue = value;
    } else if (section === 'newConfigDevices') {
      newValue = Math.max(0, Number(value));
    } else {
      newValue = value;
    }

    const updatedData = {
      ...formData,
      [section]: {
        ...formData[section],
        [key]: newValue,
      },
    };

    setFormData(updatedData);
    setJsonResult(JSON.stringify(updatedData, null, 2));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formattedData = {
      ...formData,
      availableDevices: Object.fromEntries(
        Object.entries(formData.availableDevices).map(([key, value]) => [
          key,
          value.split(',').map(item => item.trim()).filter(item => item)
        ])
      )
    };

    setJsonResult(JSON.stringify(formattedData, null, 2));

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/config/', formattedData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const rawResponse = await response.config.data;

      navigate('/response', {
        state: { 
          data: response.data, 
          rawResponse: rawResponse 
        }
      });
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <div className="form-container">
      <form onSubmit={handleSubmit}>
        <h2>New Config Devices</h2>
        {Object.keys(formData.newConfigDevices).map((device) => (
          <div key={device} className="form-group">
            <label>
              {newConfigDeviceLabels[device]}
              <input
                type="number"
                name={`newConfigDevices.${device}`}
                value={formData.newConfigDevices[device]}
                onChange={handleChange}
              />
            </label>
          </div>
        ))}

        <h2>Available Devices</h2>
        {Object.keys(formData.availableDevices).map((device) => (
          <div key={device} className="form-group">
            <label>
              {availableDeviceLabels[device]}
              <input
                type="text"
                name={`availableDevices.${device}`}
                value={formData.availableDevices[device]}
                onChange={handleChange}
              />
            </label>
          </div>
        ))}

        <h2>Properties</h2>
        {Object.keys(formData.properties).map((property) => (
          <div key={property} className="form-group">
            <label>
              {property.charAt(0).toUpperCase() + property.slice(1)}:
              <select
                name={`properties.${property}`}
                value={formData.properties[property]}
                onChange={handleChange}
              >
                <option value="NONE">NONE</option>
                <option value="LOW">LOW</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HIGH">HIGH</option>
                <option value="VERYHIGH">VERYHIGH</option>
              </select>
            </label>
          </div>
        ))}

        <button type="submit">Submit</button>
      </form>
      <h3></h3>
      <h3></h3>

    </div>
  );
}

export default Form;
