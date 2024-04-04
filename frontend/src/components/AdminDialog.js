import * as React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import RefreshIcon from '@mui/icons-material/Refresh';
import toast from 'react-hot-toast';
import { api_client, fetchToken } from '../auth';

export function NewAccountDialog(props) {

  return (
    <React.Fragment>
      <Dialog
        open={props.open}
        onClose={props.onClose}
        PaperProps={{
          component: 'form',
          onSubmit: (event) => {
            event.preventDefault();
            const formData = new FormData(event.currentTarget);
            const formJson = Object.fromEntries(formData.entries());
            api_client.put("accounts",
              {
                name: formJson.name,
                email: formJson.email,
                password: formJson.password,
              },
              {
              withCredentials: true,
              headers: {
                'Accept': 'application/json',
                'Authorization': `Bearer ${fetchToken()}`
              },
            }).then(() => {
              toast.custom(
                <Paper elevation={6}>
                  <Typography variant="h5">
                    New Account Created Successfully
                  </Typography>
                  <Button
                    endIcon={<RefreshIcon />}
                    onClick={() => {window.location.reload()}}
                  >
                    Refresh
                  </Button>
                </Paper>,
                {
                  duration: 8000,
                }
              );
            }).catch((error) => {
              if( error.response ){
                console.log(error.response.data); // => the response payload
              }
            });
            props.onClose();
          },
        }}
      >
        <DialogTitle>Add Account</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Create a new user account.
          </DialogContentText>
          <TextField
            autoFocus
            required
            margin="dense"
            id="name"
            name="name"
            label="Name"
            type="text"
            fullWidth
            variant="standard"
          />
          <br/>
          <TextField
            required
            margin="dense"
            id="email"
            name="email"
            label="Email Address"
            type="email"
            fullWidth
            variant="standard"
          />
          <br/>
          <TextField
            required
            margin="dense"
            id="password"
            name="password"
            label="Password"
            type="password"
            fullWidth
            variant="standard"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={props.onClose}>Cancel</Button>
          <Button type="submit">Create Account</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}




export function NewGroupDialog(props) {
  
    return (
      <React.Fragment>
        <Dialog
          open={props.open}
          onClose={props.onClose}
          PaperProps={{
            component: 'form',
            onSubmit: (event) => {
              event.preventDefault();
              const formData = new FormData(event.currentTarget);
              const formJson = Object.fromEntries(formData.entries());
              const email = formJson.email;
              console.log(email);
              props.onClose();
            },
          }}
        >
          <DialogTitle>Create New Submission Group</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Create a new group for submissions to use.
            </DialogContentText>
            <TextField
              autoFocus
              required
              margin="dense"
              id="name"
              name="email"
              label="Email Address"
              type="email"
              fullWidth
              variant="standard"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={props.onClose}>Cancel</Button>
            <Button type="submit">Subscribe</Button>
          </DialogActions>
        </Dialog>
      </React.Fragment>
    );
  }
