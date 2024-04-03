/*******************************************************************************
  Application Drawer
*******************************************************************************/
import * as React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import PersonIcon from '@mui/icons-material/Person';
import AllInboxIcon from '@mui/icons-material/AllInbox';
import { FixedSizeList } from 'react-window';
import { api_client, fetchToken } from '../auth';

function renderRow(props) {

  return (
    <ListItem key={props.data[props.index].id} disablePadding>
      <ListItemButton>
        <ListItemText primary={props.data[props.index].name} />
      </ListItemButton>
    </ListItem>
  );
}

export default function AdminAppDrawer(props) {
  const [groups, setGroups] = React.useState([]);

  React.useEffect(()=>{
    // Load Requisites when page Completes
    console.log(props.account)
    if (!!props.account) {
      getGroupsList(props.account.id);
    }
  },[props.account]);

  const getGroupsList = (accountId) => {
    console.log(accountId)
    if (!accountId) {
      return
    }
    api_client.get(`groups/by-account/${accountId}`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${fetchToken()}`
      },
    }).then(res => res.data).then(jsonData => {
      // Record the Groups for This Account
      setGroups(jsonData);
    })
    .catch((error) => {
      if( error.response ){
        console.log(error.response.data); // => the response payload
      }
    });
  }
  

  return (
    <>
      <Drawer
        sx={{
          width: props.drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: props.drawerWidth,
            boxSizing: 'border-box',
          },
        }}
        variant="permanent"
        anchor="left"
      >
        <Toolbar />
        <Divider />
        <List>
          <ListItem key={"accounts"} disablePadding>
            <ListItemButton>
              <ListItemIcon><PersonIcon /></ListItemIcon>
              <ListItemText primary={"Accounts"} />
            </ListItemButton>
          </ListItem>
          <ListItem key={"groups"} disablePadding>
            <ListItemButton>
              <ListItemIcon><AllInboxIcon /></ListItemIcon>
              <ListItemText primary={"Groups"} />
            </ListItemButton>
          </ListItem>
        </List>
        <Divider />
        <Box
          sx={{ width: '100%', height: 400, maxWidth: props.drawerWidth-2, bgcolor: 'background.paper' }}
        >
          <ListItem><ListItemText primary={"Submissions"}/></ListItem>
          <FixedSizeList
            height={400}
            width={props.drawerWidth-2}
            itemSize={46}
            itemData={groups}
            itemCount={groups.length}
            overscanCount={5}
          >
            {renderRow}
          </FixedSizeList>
        </Box>
        <Divider />
      </Drawer>
      <Box
        component="main"
        sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3 }}
      >
        <Toolbar />
        {props.children}
      </Box>
    </>
  );
}
