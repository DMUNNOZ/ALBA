import React from 'react';

function Configurations({ response }) {
  return (
    <div>
      <h2>Configurations</h2>
      {response ? <pre>{JSON.stringify(response, null, 2)}</pre> : <p>No data to display</p>}
    </div>
  );
}

export default Configurations;
