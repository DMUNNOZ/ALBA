import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Form from './components/Form'; 
import ResponseView from './components/ResponseView';
import Sidebar from './components/Sidebar';
import DeviceListView from './components/DeviceListView';
import DeviceForm from './components/DeviceForm';
import PropertyDetailsView from './components/PropertyDetailsView';
import './index.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<Form />} /> 
            <Route path="/response" element={<ResponseView />} /> 
            <Route path="/devices" element={<DeviceListView />} />
            <Route path="/new" element={<DeviceForm />} />
            <Route path="/info" element={<PropertyDetailsView />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;


