
import React from 'react';
import ReactDOM from 'react-dom';
import {RouterProvider, createBrowserRouter} from 'react-router-dom';
import './index.css';
import EmbedableRecorder from './Component';
import { RequireToken, fetchToken } from './auth';
import AdminApp from './App';
import LoginPortal from './login';
import SignUpPortal from './signup';

// Find all widget divs
const widgetDivs = document.querySelectorAll('.audihose-recorder-widget');

const router = createBrowserRouter([
  {
    path: "/",
    element: <RequireToken>
      <AdminApp />
    </RequireToken>
  },
  {path: "login", element: <LoginPortal />},
  {path: "sign-up", element: <SignUpPortal />},
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
} else if (!!fetchToken()) {
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(
    <React.StrictMode>
      <RouterProvider router={router} />
    </React.StrictMode>
  );
} else if (
    window.location.pathname.includes("login") || window.location.pathname.includes("sign-up")
  ) {
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(
    <React.StrictMode>
      <RouterProvider router={router} />
    </React.StrictMode>
  );
}

