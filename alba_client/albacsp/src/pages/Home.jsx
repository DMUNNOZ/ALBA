// src/pages/Home.jsx
import React, { useState } from 'react';
import Form from '../components/Form';
import Configurations from '../components/Configurations';

function Home() {
  const [response, setResponse] = useState(null);

  const handleResponse = (data) => {
    setResponse(data);
  };

  return (
    <div>
      <h1>Home</h1>
      <Form onResponse={handleResponse} />
      <Configurations response={response} />
    </div>
  );
}

export default Home;
