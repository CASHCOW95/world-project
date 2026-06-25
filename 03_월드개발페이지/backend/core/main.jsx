import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

/**
 * React entry point mounting to index.html's root div.
 */
const rootElement = document.getElementById('root');
if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}
