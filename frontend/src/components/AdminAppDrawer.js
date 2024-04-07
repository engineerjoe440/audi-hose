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
import { getGroupsListByAccount } from '../api/groups';

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
    if (!!props.account) {
      getGroupsListByAccount({accountId: props.account.id, onSet: setGroups});
    }
  },[props.account]);
  

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
            <ListItemButton onClick={() => {props.onNavigate("Accounts")}}>
              <ListItemIcon><PersonIcon /></ListItemIcon>
              <ListItemText primary={"Accounts"} />
            </ListItemButton>
          </ListItem>
          <ListItem key={"groups"} disablePadding>
            <ListItemButton onClick={() => {props.onNavigate("Groups")}}>
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
