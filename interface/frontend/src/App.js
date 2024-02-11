import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'

function App() {
  const [text, setText] = useState('');
  const [processedText, setProcessedText] = useState('');
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState('');

  const fetchMessages = async () => {
    try {
      const response = await axios.get('http://localhost:4000/read-message');
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  const handleSubmitText = async (e) => {
    e.preventDefault();
    try {
      fetchMessages();
      const response = await axios.post('/data', { text });
      setProcessedText(response.data.processed_text.response_text);
      setText('');
      setQuery(response.data.processed_text.response_text_repeated);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleSubmitQuery = async (e) => {
    e.preventDefault();
    try {
      fetchMessages();
      const response = await axios.post('/data-query', { text });
      setProcessedText(response.data.processed_text.response_text);
      setText('');
      setQuery('');
    } catch (error) {
      console.error('Error:', error);
    }
  };
    return (
      <div id='outer'>
        <h1>What health information do you need?</h1>
        <form id="question-form" onSubmit={handleSubmitText}>
          <input
            type="text"
            id="textInput"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter question"
          />
          <input type="submit" value="Submit" />
        </form>
        <form id="query-form" onSubmit={handleSubmitQuery}>
          <input
            type="text"
            id="textInput"
            value={query}
            onChange={(f) => setQuery(f.target.value)}
            placeholder="Enter query"
          />
          <input type="submit" value="Submit" />
        </form>
        <div id="output">{processedText && <p>{processedText}</p>}</div>
        <div id='most-recent'>
          <h2>Most Recent Responses:</h2>
          {messages.map((message, index) => (
            <div key={index} style={{ marginBottom: '20px' }}>
              <table>
                <tbody>
                  <tr>
                    <td><strong>Question:</strong></td>
                    <td>{message.question}</td>
                  </tr>
                  <tr>
                    <td><strong>Response:</strong></td>
                    <td>{message.response}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          ))}
        </div>
      </div>
    );
  }

export default App;