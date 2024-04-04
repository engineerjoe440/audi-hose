import * as React from 'react';
import { Box, Typography, Fab, Grid } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { CollapsibleTable } from './CollapsibleTable';
import { api_client, fetchToken } from '../auth';

export function AdminAccountsView(props) {
  const [accounts, setAccounts] = React.useState([]);

  React.useEffect(()=>{
    // Load Requisites when page Completes
    getAccountsList();
  },[]);

  const getAccountsList = () => {
    api_client.get("accounts", {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${fetchToken()}`
      },
    }).then(res => res.data).then(jsonData => {
      // Record the Accounts
      setAccounts(jsonData);
    })
    .catch((error) => {
      if( error.response ){
        console.log(error.response.data); // => the response payload
      }
    });
  }
  
  return (
    <>
      <Grid container>
        <Grid item xs={10}>
          <Typography variant='h3'>Accounts</Typography>
        </Grid>
        <Grid item xs={2}>
          <Box sx={{ '& > :not(style)': { m: 1 } }}>
            <Fab color="primary" aria-label="add">
              <AddIcon />
            </Fab>
          </Box>
        </Grid>
      </Grid>
      <br/>
      <CollapsibleTable childRows={accounts} />
    </>
  );
}
