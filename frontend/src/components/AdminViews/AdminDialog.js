import * as React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import MenuItem from '@mui/material/MenuItem';
import RefreshIcon from '@mui/icons-material/Refresh';
import toast from 'react-hot-toast';
import { api_client, fetchToken } from '../../auth';
import { getGroupsList } from '../../api/groups';

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
            api_client.put("groups",
              {
                name: formJson.name,
                accounts: [],
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
                    New Group Created Successfully
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
        <DialogTitle>Add Group</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Create a new group.
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
        </DialogContent>
        <DialogActions>
          <Button onClick={props.onClose}>Cancel</Button>
          <Button type="submit">Create Group</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
}



export function SelectGroupDialog(props) {
  const [groups, setGroups] = React.useState([]);

  React.useEffect(()=>{
    // Load Requisites when page Completes
    getGroupsList({onSet: setGroups});
  },[]);
  
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
              api_client.post(`groups/accounts/${formJson.group}?account_id=${props.account.id}`,
                {
                  withCredentials: true,
                  headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${fetchToken()}`
                  },
                }
              ).then(res => res.data).then(jsonData => {
                // Account has Been Added to Group
                toast.custom(
                  <Paper elevation={6}>
                    <Typography variant="h5">
                      Group Successfully Added
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
              })
              .catch((error) => {
                if( error.response ){
                  console.log(error.response.data); // => the response payload
                }
              });
              props.onClose();
            },
          }}
        >
          <DialogTitle>Create New Submission Group</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Create a new group for submissions to use.
            </DialogContentText>
            <Select
              required
              id="group"
              name="group"
              label="Group"
              fullWidth
            >
              {groups.map((row) => (
                <MenuItem value={row.id}>{row.name}</MenuItem>
              ))}
            </Select>
          </DialogContent>
          <DialogActions>
            <Button onClick={props.onClose}>Cancel</Button>
            <Button type="submit">Add Group</Button>
          </DialogActions>
        </Dialog>
      </React.Fragment>
    );
  }
