// src/App.jsx
import React from 'react';
import LogFilter from './components/LogFilter';
import LogDisplay from './components/LogDisplay';

function App() {
  
  return (
    <div className="App">
      <h1>Log Viewer</h1>
      <LogFilter />
      <LogDisplay />
    </div>
  );
}

export default App;