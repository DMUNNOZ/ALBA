import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './DeviceForm.css';

const DeviceForm = () => {
  const initialState = {
    model: '',
    type: '',
    capability: '',
    impact: null,
    risk: null,
    sustainability: null,
    home: null,
    vulnerabilities: [],
    apps: [],
    power_supplies: [],
    connectivities: [],
  };

  const [formData, setFormData] = useState(initialState);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name === 'impact' || name === 'risk' || name === 'sustainability') {
      setFormData({
        ...formData,
        [name]: value !== '' ? parseFloat(value) : null,
      });
    } else if (name === 'home') {
      setFormData({
        ...formData,
        [name]: value !== '' ? parseInt(value, 10) : null,
      });
    } else if (['vulnerabilities', 'apps', 'power_supplies', 'connectivities'].includes(name)) {
      setFormData({
        ...formData,
        [name]: value.split(',').map((item) => item.trim()).filter((item) => item),
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/devices/', formData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      navigate('/devices', {
        state: { 
          data: response.data 
        }
      });
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <div className="device-form-container">
      <form onSubmit={handleSubmit}>
        <h2>Create New Device</h2>

        <div className="form-group">
          <label>
            Model:
            <input
              type="text"
              name="model"
              value={formData.model}
              onChange={handleChange}
              required
            />
          </label>
        </div>

        <div className="form-group">
          <label>
            Type:
            <input
              type="text"
              name="type"
              value={formData.type}
              onChange={handleChange}
              required
            />
          </label>
        </div>

        <div className="form-group">
          <label>
            Capability:
            <input
              type="text"
              name="capability"
              value={formData.capability}
              onChange={handleChange}
              required
            />
          </label>
        </div>

        <div className="form-group">
          <label>
            Impact (optional):
            <input
              type="number"
              step="any"
              name="impact"
              value={formData.impact || ''}
              onChange={handleChange}
            />
          </label>
        </div>

        <div className="form-group">
          <label>
            Risk (optional):
            <input
              type="number"
              step="any"
              name="risk"
              value={formData.risk || ''}
              onChange={handleChange}
            />
          </label>
        </div>

        <div className="form-group">
          <label>
            Sustainability (optional):
            <input
              type="number"
              step="any"
              name="sustainability"
              value={formData.sustainability || ''}
              onChange={handleChange}
            />
          </label>
        </div>

        <div className="form-group">
          <label>
            Home (optional):
            <input
              type="number"
              name="home"
              value={formData.home || ''}
              onChange={handleChange}
            />
          </label>
        </div>

        <div className="form-group">
          <label>
            Vulnerabilities (comma separated):
            <input
              type="text"
              name="vulnerabilities"
              value={formData.vulnerabilities.join(', ')}
              onChange={handleChange}
            />
          </label>
        </div>

        <div className="form-group">
          <label>
            Apps (comma separated):
            <input
              type="text"
              name="apps"
              value={formData.apps.join(', ')}
              onChange={handleChange}
            />
          </label>
        </div>

        <div className="form-group">
          <label>
            Power Supplies (comma separated):
            <input
              type="text"
              name="power_supplies"
              value={formData.power_supplies.join(', ')}
              onChange={handleChange}
            />
          </label>
        </div>

        <div className="form-group">
          <label>
            Connectivities (comma separated):
            <input
              type="text"
              name="connectivities"
              value={formData.connectivities.join(', ')}
              onChange={handleChange}
            />
          </label>
        </div>

        <button type="submit">Create Device</button>
      </form>

      <pre>{JSON.stringify(formData, null, 2)}</pre>
    </div>
  );
};

export default DeviceForm;
