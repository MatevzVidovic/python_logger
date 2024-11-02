




// src/components/LogDisplay.js
import React, { useState, useEffect } from 'react';


// Line component to display a single line of text
const Line = ({text, cutoff_length}) => {
    const [isExpanded, setIsExpanded] = useState(false);
  
    // Toggle the expanded state
    const toggleExpand = () => {
      setIsExpanded(!isExpanded);
    };
  
    // Determine the text to display based on the expanded state
    const displayText = isExpanded ? text : text.slice(0, cutoff_length);
  
    return (
      <div onClick={toggleExpand} style={{ cursor: 'pointer', marginBottom: '10px' }}>
        {displayText}
        {!isExpanded && text.length > cutoff_length && '...'}
      </div>
    );
}
  
// Main component to split text and render Line components
const TextSplitter = ({lineText, cutoff_length}) => {
    // Split the text by newline characters
    const lines = lineText.split('\n');
  
    return (
      <div>
        {lines.map((line, index) => (
          <Line key={index} text={line} cutoff_length={cutoff_length} />
        ))}
      </div>
    );
}
  

const SingleLog = (lineText, logType, functionNumber, index, cutoff_length) => {

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
        case '@manual_log':
            return 'rgb(54, 162, 235)'; // Blue
        case '@stack_log':
            return 'rgb(153, 102, 255)'; // Purple
        default:
            return 'rgb(220, 53, 69)'; // Red
        }
    };

  return (
    
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
        <TextSplitter lineText={lineText} cutoff_length={cutoff_length} />
    </div>
      
  );
};

export default SingleLog;