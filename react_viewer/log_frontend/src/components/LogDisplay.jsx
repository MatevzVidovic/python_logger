// src/components/LogDisplay.js
import React, { useState, useEffect } from 'react';
import SingleLog from './SingleLog';

const LogDisplay = () => {
  const [logs, setLogs] = useState([]);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(1000); // Number of logs per page
  const [cutoffLength, setCutoffLength] = useState(100);
  const [allShortened, setAllShortened] = useState(true);
  const [error, setError] = useState(null);


  const fetchLogs = () => {
    fetch(`http://localhost:5000/logs?page=${page}&per_page=${perPage}`)
      .then(response => response.json())
      .then(
        (data) => {
          setLogs(data);
          // console.log("data", data);
          // len of data
          console.log("len of data", data.length);
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

  const handleAllShortenedChange = () => {
    setAllShortened(!allShortened);
  };


  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div className="log-container">
      <div>
        <label>Set new cutoff length (length of text of a var or arg where the text stops unless you click on it):</label>
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
      <button onClick={handleAllShortenedChange}>
        {allShortened ? 'Expand All' : 'Shorten All'}
      </button>
      <div className="pagination-controls">
        <button onClick={handlePreviousPage} disabled={page === 1}>Previous</button>
        <button onClick={handleNextPage}>Next</button>
      </div>
      <div>
        Num of logs on page: {logs.length}
      </div>
      {logs.map(([lineText, logType, functionNumber], index) => (
        <SingleLog
          key={index}
          lineText={lineText}
          logType={logType}
          functionNumber={functionNumber}
          index={index}
          cutoff_length={cutoffLength}
          allShortened={allShortened}
        />
      ))}
      <button onClick={fetchLogs}>Refresh Logs</button>
      <button onClick={handleAllShortenedChange}>
        {allShortened ? 'Expand All' : 'Shorten All'}
      </button>
      <div className="pagination-controls">
        <button onClick={handlePreviousPage} disabled={page === 1}>Previous</button>
        <button onClick={handleNextPage}>Next</button>
      </div>
    </div>
  );
};

export default LogDisplay;