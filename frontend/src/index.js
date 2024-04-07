
import React from 'react';
import ReactDOM from 'react-dom';
import {RouterProvider, createBrowserRouter} from 'react-router-dom';
import './index.css';
import EmbedableRecorder from './Component';
import { RequireToken } from './auth';
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

widgetDivs.forEach(div => {
  ReactDOM.render(
    <React.StrictMode>
      <EmbedableRecorder
        color={div.dataset.color}
        prompt={div.dataset.prompt}
        groupId={div.dataset.groupId}
      />
    </React.StrictMode>,
      div
  );
});
const rootElement = document.getElementById('root');
if (!!rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <RouterProvider router={router} />
    </React.StrictMode>
  );
}

