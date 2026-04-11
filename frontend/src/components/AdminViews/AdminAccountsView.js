import * as React from 'react';
import { Box, Typography, Fab } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { CollapsibleTable } from '../CollapsibleTable';
import { NewAccountDialog } from './AdminDialog';
import { api_client, fetchToken } from '../../auth';

export function AdminAccountsView(props) {
  const [accounts, setAccounts] = React.useState([]);
  const [newAccountOpen, setNewAccountOpen] = React.useState(false);

  React.useEffect(()=>{
    // Load Requisites when page Completes
    getAccountsList();
  },[]);

  const getAccountsList = () => {
    api_client.get("accounts/with-groups", {
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
      <NewAccountDialog open={newAccountOpen} onClose={() => {setNewAccountOpen(false)}}/>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant='h3'>Accounts</Typography>
        <Fab color="primary" aria-label="add" onClick={() => {setNewAccountOpen(true)}}>
          <AddIcon />
        </Fab>
      </Box>
      <CollapsibleTable childRows={accounts} />
    </>
  );
}
