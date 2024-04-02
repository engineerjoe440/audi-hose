
import React from 'react';
import ReactDOM from 'react-dom';
import {RouterProvider, createBrowserRouter} from 'react-router-dom';
import './index.css';
import EmbedableRecorder from './Component';
import LoginPortal from './login';
import { RequireToken } from './auth';

// Find all widget divs
const widgetDivs = document.querySelectorAll('.audihose-recorder-widget');

const router = createBrowserRouter([
  {path: "login", element: <LoginPortal />},
]);

if (window.location.pathname.includes("component")) {
  // Component Code
  // Inject our React EmbedableRecorder into each class
  widgetDivs.forEach(div => {
    ReactDOM.render(
      <React.StrictMode>
        <EmbedableRecorder
          color={div.dataset.color}
          prompt={div.dataset.prompt}
        />
      </React.StrictMode>,
        div
    );
  });
} else {
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(
    <React.StrictMode>
      <RouterProvider router={router} />
    </React.StrictMode>
  );
}

