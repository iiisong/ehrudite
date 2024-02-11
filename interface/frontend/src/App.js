import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css'

function App() {
  const [text, setText] = useState('');
  const [processedText, setProcessedText] = useState('');
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState([]);
  const [relqs, setRelqs] = useState([]);

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
      setProcessedText(response.data.results);
      setText('');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleSubmitQuery = async (e) => {
    e.preventDefault();
    try {
      fetchMessages();
      const response = await axios.post('/data-query', { text });
      setProcessedText(response.data.results);
      setQuery('');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleDropdownClick = (index) => {
    const updatedMessages = [...messages];
    updatedMessages[index].isOpen = !updatedMessages[index].isOpen;
    setMessages(updatedMessages);
  };

  return (
    <div>
      <h1>What health information do you need?</h1>
      <form id="form1" onSubmit={handleSubmitText}>
        <input
          type="text"
          id="textInput"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Enter text"
        />
        <input type="submit" value="Submit" />
      </form>
      <form id="form2" onSubmit={handleSubmitQuery}>
        <input
          type="text"
          id="textInput"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter query"
        />
        <input type="submit" value="Submit" />
      </form>
      <div id="output">{processedText && <p>{processedText}</p>}</div>
      <div>
      <h2>Most Recent Responses:</h2>
        <ol>
          {messages.map((message, index) => (
            <li key={index}>
              <div onClick={() => handleDropdownClick(index)}>
                <strong>{message.question}: {message.query}</strong>
              </div>
              {message.isOpen && <p>{message.response}</p>}
            </li>
          ))}
        </ol>
      </div>
      <div>
      <h2>Relevant Responses:</h2>
      <ol>
          {relqs?.map((relq, index) => (
            <li key={index}>
              <div onClick={() => handleDropdownClick(index)}>
                <strong>{relq.question}</strong>
              </div>
              {relq.isOpen && <p>{relq.query}</p>}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}

export default App;