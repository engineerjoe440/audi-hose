import * as React from 'react';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { ThemeProvider } from '@mui/material/styles';
import toast from 'react-hot-toast';
import { Copyright, client, theme } from './login';
import { setToken } from './auth';

export default function SignUpPortal() {
    const handleSubmit = (event) => {
        event.preventDefault();
        const data = new FormData(event.currentTarget);
        console.log(window.client_token)

        client.post("create-initial-account", {
          name: data.get('name'),
          email: data.get('email'),
          password: data.get('password'),
          client_token: window.client_token,
        }).then((response) => {
          console.log(response);
          if (response.data.message !== null) {
            toast.error(response.data.message);
          } else if (response.data.token !== null) {
            setToken(response.data.token);

            // Redirect to Admin
            window.location.href = "/";
          }
        })
        .catch((error) => {
          if (error.response.status === 410 ){
            if (String(error.response.data.detail).includes('please reload')) {
              toast.error("Please Reload Page.")
            } else {
              toast.error("Server Failure, Please Try Again.")
            }
            if( error.response ){
              console.log(error.response.data); // => the response payload
            }
          } else if (error.response.status === 401) {
            if (String(error.response.data.detail.toLowerCase()).includes('email')) {
              toast.error(error.response.data.detail)
            } else {
              toast.error("Server Failure, Please Try Again.")
            }
          } else if (error.response.status === 403) {
            if (String(error.response.data.detail.toLowerCase()).includes('email')) {
              toast.error(error.response.data.detail)
            } else {
              toast.error("Server Failure, Please Try Again.")
            }
          } else {
            toast.error("Failed to communicate with authentication service.")
            if( error.response ){
              console.log(error.response.data); // => the response payload
            }
          }
        });
      };

  return (
    <ThemeProvider theme={theme}>
      <Container component="main" maxWidth="xs">
        <CssBaseline />
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component="h1" variant="h5">
            Create Admin Account
          </Typography>
          <Box component="form" noValidate onSubmit={handleSubmit} sx={{ mt: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={12}>
                <TextField
                  autoComplete="name"
                  name="name"
                  required
                  fullWidth
                  id="name"
                  label="Name"
                  autoFocus
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  id="email"
                  label="Email Address"
                  name="email"
                  autoComplete="email"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type="password"
                  id="password"
                  autoComplete="new-password"
                />
              </Grid>
            </Grid>
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
            >
              Sign Up
            </Button>
          </Box>
        </Box>
        <Copyright sx={{ mt: 5 }} />
      </Container>
    </ThemeProvider>
  );
}
