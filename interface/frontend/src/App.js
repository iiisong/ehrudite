import React, { useState } from 'react';
import axios from 'axios';
import './App.css'

function App() {
  const [text, setText] = useState('');
  const [processedText, setProcessedText] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/data', { text });
      setProcessedText(response.data.processed_text);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      <h1>What health information do you need?</h1>
      <form id="myForm" onSubmit={handleSubmit}>
        <input
          type="text"
          id="textInput"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text"
        />
        <input type="submit" value="Submit" />
      </form>
      <div id="output">{processedText && <p>{processedText}</p>}</div>
    </div>
  );
}

export default App;