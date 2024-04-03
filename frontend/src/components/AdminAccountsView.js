import * as React from 'react';
import { Typography } from '@mui/material';
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
      <Typography variant='h3'>Accounts</Typography>
      <br/>
      <CollapsibleTable childRows={accounts} />
    </>
  );
}
