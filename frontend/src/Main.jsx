import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';    // The app shell with routes
import './index.css';          // Your global styles (Tailwind, etc.)

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
