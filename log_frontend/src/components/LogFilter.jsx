import React, { useState } from 'react';

const LogFilter = ({ refreshLogDisplay }) => {
  const [inputValue, setInputValue] = useState('');

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const sendRequest = (content) => {
    fetch('http://localhost:5000/required_content', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: content }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  const handleSendContent = () => {
    sendRequest(inputValue);
  };

  const handleNullifyContent = () => {
    sendRequest('');
  };


  return (
    <div>
      <input
        type="text"
        value={inputValue}
        onChange={handleInputChange}
        placeholder="Required text contents"
      />
      <button onClick={handleSendContent}>Send Content</button>
      <button onClick={handleNullifyContent}>Nullify Content Requirements</button>
    </div>
  );
};

export default LogFilter;