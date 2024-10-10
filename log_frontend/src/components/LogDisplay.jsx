// src/components/LogDisplay.js
import React, { useState, useEffect } from 'react';

const LogDisplay = () => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/logs')
      .then(response => response.json())
      .then(data => setLogs(data));
  }, []);

  const getColorForFunctionNumber = (number) => {
    // Generate a color based on the function number
    // This is a simple hash function, you can replace it with a more sophisticated one
    const hue = Math.abs(number * 31) % 360;
    return `hsl(${hue}, 70%, 30%)`;
  };

  const getColorForLogType = (type) => {
    switch (type) {
      case '@autolog':
        return 'rgb(255, 165, 0)'; // Orange
      case '@local_log':
        return 'rgb(75, 192, 192)'; // Light Blue
      default:
        return 'rgb(220, 53, 69)'; // Red
    }
  };

  return (
    <div className="log-container">
      {logs.map(([lineText, logType, functionNumber], index) => (
        <div
          key={index}
          style={{
            backgroundColor: getColorForFunctionNumber(functionNumber),
            borderLeft: `50px solid ${getColorForLogType(logType)}`,
            padding: '10px',
            margin: '5px 0',
            whiteSpace: 'pre-wrap',
          }}
        >
          {lineText}
        </div>
      ))}
    </div>
  );
};

export default LogDisplay;