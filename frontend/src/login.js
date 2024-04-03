/*******************************************************************************
 * login.js
 * 
 * Authentication page view.
 ******************************************************************************/

import * as React from 'react';
import {
  Avatar,
  Alert,
  Button,
  CssBaseline,
  TextField,
  Link,
  Box,
  Grid,
  Typography,
  FormControlLabel,
  Checkbox,
  Paper,
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { getDesignTokens, getSavedThemeMode } from "./theme";
import { fetchToken, setToken, refreshTokenCall } from './auth';
import axios from "axios";

export const client = axios.create({
  baseURL: "/" 
});

export function Copyright(props) {

  return (
    <Typography variant="body2" color="text.secondary" align="center" {...props}>
      {'Copyright © '}
      <Link color="inherit" href="https://stanleysolutionsnw.com">
        Stanley Solutions
      </Link>{' '}
      {new Date().getFullYear()}
      {'.'}
    </Typography>
  );
}

export const theme = createTheme(getDesignTokens(getSavedThemeMode()));

export default function LoginPortal() {
  refreshTokenCall({redirect: false});
  const [loginAlert, setLoginAlert] = React.useState("");
  const [signupRequired, setSignupRequired] = React.useState(null);

  React.useEffect(()=>{
    // Redirect if Auth is Valid
    refreshTokenCall({redirect: false});
    if (!!fetchToken()){
      window.location.href = "/";
    }
    // Redirect if No Accounts are Present
    if (signupRequired) {
      window.location.href = "/sign-up";
    } else {
      fetchSignupStatus();
    }
  },[signupRequired]);

  const fetchSignupStatus = () => {
    fetch("/signup-required", {
      method: "GET",
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Cookie': `client_token=${window.client_token}`,
      },
    }).then(res => {
      res.json().then(jsonData => {
        // Store the Signup Status
        setSignupRequired(jsonData);
      })
    }).catch(res => {
      console.log(res);
    })
  }

  const handleSubmit = (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    console.log(window.client_token)

    client.post("login", {
      email: data.get('email'),
      password: data.get('password'),
      client_token: window.client_token,
    }).then((response) => {
      console.log(response);
      if (response.data.message !== null) {
        setLoginAlert(response.data.message);
      } else if (response.data.token !== null) {
        setToken(response.data.token);
        setLoginAlert("");

        // Redirect to Admin
        window.location.href = "/";
      }
    })
    .catch((error) => {
      if (error.response.status === 410 ){
        if (String(error.response.data.detail).includes('please reload')) {
          setLoginAlert("Please Reload Page.")
        } else {
          setLoginAlert("Server Failure, Please Try Again.")
        }
        if( error.response ){
          console.log(error.response.data); // => the response payload
        }
      } else if (error.response.status === 401) {
        if (String(error.response.data.detail.toLowerCase()).includes('email')) {
          setLoginAlert(error.response.data.detail)
        } else {
          setLoginAlert("Server Failure, Please Try Again.")
        }
      } else if (error.response.status === 403) {
        if (String(error.response.data.detail.toLowerCase()).includes('email')) {
          setLoginAlert(error.response.data.detail)
        } else {
          setLoginAlert("Server Failure, Please Try Again.")
        }
      } else {
        setLoginAlert("Failed to communicate with authentication service.")
        if( error.response ){
          console.log(error.response.data); // => the response payload
        }
      }
    });
  };

  return (
    <ThemeProvider theme={theme}>
      <Grid container component="main" sx={{ height: '100vh' }}>
        <CssBaseline />
        <Grid
          item
          xs={false}
          sm={4}
          md={7}
          sx={{
            backgroundImage: 'url(/static/react/audihose-logo.png)',
            backgroundRepeat: 'no-repeat',
            backgroundColor: (t) =>
              t.palette.mode === 'light' ? t.palette.grey[50] : t.palette.grey[900],
            backgroundSize: 'contain',
            backgroundPosition: 'center',
          }}
        />
        <Grid item xs={12} sm={8} md={5} component={Paper} elevation={6} square>
          <Box
            sx={{
              my: 8,
              mx: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
              <LockOutlinedIcon />
            </Avatar>
            <Typography component="h1" variant="h6">
              Connecting audiences to the creators they love.
            </Typography>
            {loginAlert.length > 0 &&
              <Alert severity="error">
                <span style={{ whiteSpace: 'pre-line' }}>{loginAlert}</span>
              </Alert>
            }
            <Box component="form" noValidate onSubmit={handleSubmit} sx={{ mt: 1 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                autoComplete="email"
                autoFocus
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
              />
              <FormControlLabel
                control={<Checkbox value="remember" color="primary" />}
                label="Remember me"
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
              >
                Sign In
              </Button>
              <Copyright sx={{ mt: 5 }} />
            </Box>
          </Box>
        </Grid>
      </Grid>
    </ThemeProvider>
  );
}