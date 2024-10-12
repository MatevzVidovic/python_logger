import React, { useState } from 'react';

const LogFilter = ({ refreshLogDisplay }) => {
  const [inputValue, setInputValue] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [regexList, setRegexList] = useState([]);

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const toggleActiveState = () => {
    setIsActive(!isActive);
  };

  const addRegex = () => {
    if (inputValue.trim()) {
      setRegexList([...regexList, { regex: inputValue.trim(), contain: isActive }]);
      setInputValue('');
    }
  };

  const removeRegex = (index) => {
    setRegexList(regexList.filter((_, i) => i !== index));
  };

  const sendRequest = (regexs) => {
    fetch('http://localhost:5000/required_regexs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ regexs }),
    })
      .then(response => response.json())
      .then(data => {
        console.log('Success:', data);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  const handleSendRegex = () => {
    sendRequest(regexList);
  };


  return (
    <div>
      <input
        type="text"
        value={inputValue}
        onChange={handleInputChange}
        placeholder="Enter regex pattern"
      />
      <button onClick={toggleActiveState}>
        {isActive ? 'contain' : 'not-contain'}
      </button>
      <button onClick={addRegex}>Add Regex</button>
      <button onClick={handleSendRegex}>Send Current Regex</button>
      <div>
        {regexList.map((item, index) => (
          <div key={index} style={{ display: 'flex', alignItems: 'center' }}>
            <span>{item.regex} - {item.contain ? 'contain' : 'not-contain'}</span>
            <button onClick={() => removeRegex(index)}>×</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LogFilter;