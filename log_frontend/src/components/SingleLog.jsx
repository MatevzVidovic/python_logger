




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
    const startingLines = lineText.split('[START_VAR]');
    
    var lines = [];
    var isVar = [];

    for (var i = 0; i < startingLines.length; i++) {
      
      // the 2 in the split function means that the max number of splits is 2, so if every [START_VAR] has an [END_VAR]
      // then we can have other stuff than VARs printed out before the next [START_VAR].
      var curr_split = startingLines[i].split('[END_VAR]', 2)

      // If there is no [END_VAR] then we aren't in a VAR block.
      // If there is one, we also need to handle the case where there is nothing after the [END_VAR] so we don't print an empty line.
      // And also, when there is something after the [END_VAR], and that thing is specifically ", \n", we want to join that into one string.
      // Just using ", \n" doesn't work. So we console logged curr_split[1] and put what it gave us into a multiline string.
      const multilineEquivalent = `, 
 `
      
      var isVarAppender = []
      if (curr_split.length == 1) {
        isVarAppender = [false]
      } else if (curr_split.length == 2) {
        
        if (curr_split[1] == '') {
          curr_split.pop() //removes last element
          isVarAppender = [true]
          // console.log(curr_split)
        } else {
          
          // console.log(curr_split[1])
          
          if (curr_split[1] == multilineEquivalent) {
            curr_split[0] = curr_split[0] + ", "
            curr_split.pop()
            isVarAppender = [true]
          } else {
            isVarAppender = [true, false]
          }
        }

      } else {
        throw new Error("Number of splits is wrong!");
      }

      // The ... means that push will extend the array final_lines, not append the new array itself
      lines.push(...curr_split);
      isVar.push(...isVarAppender);
    }

    var set_of_VAR_ixs = new Set();
    for (var i = 0; i < isVar.length; i++) {
      if (isVar[i]) {
        set_of_VAR_ixs.add(i);
      }
    }

    
    const renderLine = (line, index) => {
      if (set_of_VAR_ixs.has(index)) {
        return <Line key={index} text={line} cutoff_length={cutoff_length} />
      } else {
        return (
          <div key={index}>
            {line}
          </div>
        )
      }
    };
  
    return (
      <div>
        {lines.map(renderLine)}
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
          return 'rgb(220, 53, 69)'; // Red
        default:
            return 'rgb(153, 102, 255)'; // Purple
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