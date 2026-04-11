/*******************************************************************************
 * Admin API Support System
 ******************************************************************************/
import axios from "axios";
import { useLocation, Navigate } from "react-router-dom"

// Use Window Location to Derive Appropriate Protocol
const baseURL = new URL(window.location.origin);
baseURL.pathname = "/api/v1";

export const api_client = axios.create({baseURL: baseURL.href});

const TOKEN_NAME = 'audi-hose-token';

export const setToken = (token) => {
   localStorage.setItem(TOKEN_NAME, token);
}

export const fetchToken = () => {
   return localStorage.getItem(TOKEN_NAME);
}

export const clearToken = () => {
   localStorage.removeItem(TOKEN_NAME);
}

function isSecureRedirectPath(pathname) {
  return pathname === "/";
}

export function sanitizeRedirectTarget(target) {
  if (!target) {
    return null;
  }

  try {
    const url = new URL(target, window.location.origin);

    if (url.origin !== window.location.origin || !isSecureRedirectPath(url.pathname)) {
      return null;
    }

    return `${url.pathname}${url.search}${url.hash}`;
  } catch (error) {
    return null;
  }
}

function getLoginRedirectUrl() {
  const params = new URLSearchParams(window.location.search);
  const existingRedirect = sanitizeRedirectTarget(params.get("redirect"));
  const currentPath = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  const currentSecureRedirect = sanitizeRedirectTarget(currentPath);
  const redirectTarget = existingRedirect || currentSecureRedirect;

  if (!redirectTarget) {
    return "/login";
  }

  return `/login?redirect=${encodeURIComponent(redirectTarget)}`;
}

export function getPostLoginRedirectTarget(defaultTarget = "/") {
  const params = new URLSearchParams(window.location.search);
  return sanitizeRedirectTarget(params.get("redirect")) || defaultTarget;
}

export function refreshTokenCall({
  redirect=true,
}) {
  fetch("/refresh-token", {
    method: "POST",
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${fetchToken()}`,
      'Cookie': `client_token=${window.client_token}`,
    },
    body: '{}',
  }).then(res => {
    if ( res.status === 401 ){
      // Timed Out? Goodbye! Go back to start.
      clearToken();
      if (redirect) {
        window.location.href = getLoginRedirectUrl();
      }
      console.log(res.data);
    } else if ( res.status === 403 ) {
      // Timed Out? Goodbye! Go back to start.
      clearToken();
      if (redirect) {
        window.location.href = getLoginRedirectUrl();
      }
      console.log(res);
    } else {
      res.json().then(jsonData => {
        // Store the Updated Token
        setToken(jsonData.token);
      })
    }
  }).catch((error) => {
    if (error.response.status === 401 ){
        clearToken();
    } else if (error.response.status === 403 ){
        clearToken();
    }
    if( error.response ){
      console.log(error.response.data); // => the response payload
    }
    if (redirect) {
      window.location.href = getLoginRedirectUrl();
    }
    return Promise.reject(error.message);
  });
}

export function logout() {
  fetch("/logout", {
    method: "POST",
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${fetchToken()}`,
      'Cookie': `client_token=${window.client_token}`,
    },
    body: '{}'
  }).then(res => {
    clearToken();
    window.location.href = "/";
  }).catch((error) => {
    if (error.response.status === 401 ){
        clearToken();
    } else if (error.response.status === 403 ){
        clearToken();
    }
    if( error.response ){
      console.log(error.response.data); // => the response payload
    }
    window.location.href = "/login";
    return Promise.reject(error.message);
  });
}

api_client.interceptors.request.use((config) => {
  config.headers.Authorization = `Bearer ${fetchToken()}`;
  config.headers.Cookie = `client_token=${window.client_token}`;
  return config;
}, (error) => {
  return Promise.reject(error);
});

api_client.interceptors.response.use((response) => {
  refreshTokenCall({redirect: true});

  // Return the Regular Response
  return response;
});

export function RequireToken({children}){

   refreshTokenCall({redirect: true});
   let auth = fetchToken();
   let location = useLocation()

   if (!auth) {
      return <Navigate to='/login' state ={{from : location}}/>;
   }

   return children;
}
