// src/components/LogDisplay.js
import React, { useState, useEffect } from 'react';
import SingleLog from './SingleLog';

const LogDisplay = () => {
  const [logs, setLogs] = useState([]);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(1000); // Number of logs per page
  const [cutoffLength, setCutoffLength] = useState(100);
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

  const handleCutoffLengthChange = (event) => {
    setCutoffLength(Number(event.target.value));
  };


  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div className="log-container">
      <div>
        <label>Set new cutoff length (length of line where the line stops unless you click on it):</label>
        <input
          type="number"
          value={cutoffLength}
          onChange={handleCutoffLengthChange}
          min="1"
        />
      </div>
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
        SingleLog(lineText, logType, functionNumber, index, cutoffLength)
      ))}
      <div className="pagination-controls">
        <button onClick={handlePreviousPage} disabled={page === 1}>Previous</button>
        <button onClick={handleNextPage}>Next</button>
      </div>
    </div>
  );
};

export default LogDisplay;