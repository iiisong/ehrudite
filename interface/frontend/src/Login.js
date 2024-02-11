// Login.js
import React, { useState } from 'react';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = (e) => {
    e.preventDefault();
    // Perform authentication logic here (e.g., check credentials)
    // For simplicity, let's just check if the username and password are not empty
    if (username.trim() !== '' && password.trim() !== '') {
      setIsLoggedIn(true);
      alert('Logged in successfully!');
    } else {
      alert('Please enter a valid username and password.');
    }
  };

  return (
    <div>
      <h2>Login Page</h2>
      {isLoggedIn ? (
        <div>
          <p>Welcome, {username}!</p>
          <button onClick={() => setIsLoggedIn(false)}>Logout</button>
        </div>
      ) : (
        <form onSubmit={handleLogin}>
          <div>
            <label>Username:</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
          <div>
            <label>Password:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <button type="submit">Login</button>
        </form>
      )}
    </div>
  );
}

export default Login;
