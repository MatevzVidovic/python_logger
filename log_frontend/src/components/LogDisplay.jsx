// src/components/LogDisplay.js
import React, { useState, useEffect } from 'react';

const LogDisplay = () => {
  const [logs, setLogs] = useState([]);
  const [page, setPage] = useState(1);
  const [error, setError] = useState(null);
  const perPage = 10; // Number of logs per page

  
  const fetchLogs = () => {
    fetch(`http://localhost:5000/logs?page=${page}&per_page=${perPage}`)
      .then(response => response.json())
      .then(
        (data) => {
          setLogs(data);
        }
      )
      .catch((error) => {
        console.error('Error fetching logs:', error);
        setError(error);
      });
  };

  useEffect(() => {
    fetchLogs();
  }, [page]);

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

  const handleNextPage = () => {
    setPage(prevPage => prevPage + 1);
  };

  const handlePreviousPage = () => {
    setPage(prevPage => Math.max(prevPage - 1, 1));
  };

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div className="log-container">
      <button onClick={fetchLogs}>Refresh Logs</button>
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
      <div className="pagination-controls">
        <button onClick={handlePreviousPage} disabled={page === 1}>Previous</button>
        <button onClick={handleNextPage}>Next</button>
      </div>
    </div>
  );
};

export default LogDisplay;