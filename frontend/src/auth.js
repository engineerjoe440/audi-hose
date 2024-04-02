/*******************************************************************************
 * Admin API Support System
 ******************************************************************************/
import axios from "axios";
import { useLocation, Navigate } from "react-router-dom"

// Use Window Location to Derive Appropriate Protocol
const baseURL = new URL(window.location.origin);
baseURL.pathname = "/api/v1";

export const api_client = axios.create({baseURL: baseURL.href});

export function refreshTokenCall({
  redirect=true,
}) {
  fetch("/refresh-token", {
    method: "POST",
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${window.session_auth}`,
      'Cookie': `client_token=${window.session_token}`,
    },
    body: '{}',
  }).then(res => {
    if ( res.status === 401 ){
      // Timed Out? Goodbye! Go back to start.
      window.session_auth = null;
      if (redirect) {
        window.location.href = "/login";
      }
      console.log(res.data);
    } else if ( res.status === 403 ) {
      // Timed Out? Goodbye! Go back to start.
      window.session_auth = null;
      if (redirect) {
        window.location.href = "/login";
      }
      console.log(res);
    } else {
      res.json().then(jsonData => {
        // Store the Updated Token
        window.session_auth = jsonData.token;
      })
    }
  }).catch((error) => {
    if (error.response.status === 401 ){
        window.session_auth = null;
    } else if (error.response.status === 403 ){
        window.session_auth = null;
    }
    if( error.response ){
      console.log(error.response.data); // => the response payload
    }
    if (redirect) {
      window.location.href = "/login";
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
      'Authorization': `Bearer ${window.session_auth}`,
      'Cookie': `client_token=${window.session_token}`,
    },
    body: '{}'
  }).then(res => {
    window.session_auth = null;
    window.location.href = "/login";
  }).catch((error) => {
    if (error.response.status === 401 ){
        window.session_auth = null;
    } else if (error.response.status === 403 ){
        window.session_auth = null;
    }
    if( error.response ){
      console.log(error.response.data); // => the response payload
    }
    window.location.href = "/login";
    return Promise.reject(error.message);
  });
}

api_client.interceptors.request.use((config) => {
  config.headers.Authorization = `Bearer ${window.session_auth}`;
  config.headers.Cookie = `client_token=${window.session_token}`;
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
   let auth = window.session_auth;
   let location = useLocation()

   if (!auth) {
      return <Navigate to='/login' state ={{from : location}}/>;
   }

   return children;
}