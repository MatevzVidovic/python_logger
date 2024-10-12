// src/components/LogDisplay.js
import React, { useState, useEffect } from 'react';

const LogDisplay = () => {
  const [logs, setLogs] = useState([]);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(1000); // Number of logs per page
  const [error, setError] = useState(null);


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

  const handlePageNumberChange = (event) => {
    setPage(Number(event.target.value));
  };

  const handlePerPageChange = (event) => {
    setPerPage(Number(event.target.value));
  };

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div className="log-container">
      <div>
        <label>Go to Page:</label>
        <input
          type="number"
          value={page}
          onChange={handlePageNumberChange}
          min="1"
        />
      </div>
      <div>
        <label>Logs Per Page:</label>
        <input
          type="number"
          value={perPage}
          onChange={handlePerPageChange}
          min="1"
        />
      </div>
      <button onClick={fetchLogs}>Refresh Logs</button>
      <div className="pagination-controls">
        <button onClick={handlePreviousPage} disabled={page === 1}>Previous</button>
        <button onClick={handleNextPage}>Next</button>
      </div>
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