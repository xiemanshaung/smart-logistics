import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// Vite 入口：将 <App /> 挂载到 index.html 中的 root
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)