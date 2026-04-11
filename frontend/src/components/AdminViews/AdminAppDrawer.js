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
import Tooltip from '@mui/material/Tooltip';
import PersonIcon from '@mui/icons-material/Person';
import AllInboxIcon from '@mui/icons-material/AllInbox';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import { getGroupsListByAccount } from '../../api/groups';


export default function AdminAppDrawer(props) {
  const theme = useTheme();
  const isCompact = useMediaQuery(theme.breakpoints.down('md'));
  const compactDrawerWidth = 72;
  const activeDrawerWidth = isCompact ? compactDrawerWidth : props.drawerWidth;
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
          width: activeDrawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: activeDrawerWidth,
            boxSizing: 'border-box',
            overflowX: 'hidden',
            overflowY: 'hidden',
          },
        }}
        variant="permanent"
        open
        anchor="left"
      >
        <Toolbar />
        <Divider />
        <List>
          <ListItem key={"accounts"} disablePadding>
            <Tooltip title={isCompact ? 'Accounts' : ''} placement="right">
              <ListItemButton
                onClick={() => {props.onNavigate({page: "Accounts"})}}
                sx={{ justifyContent: isCompact ? 'center' : 'flex-start', px: 1.5 }}
              >
                <ListItemIcon sx={{ minWidth: 0, mr: isCompact ? 0 : 1.5, justifyContent: 'center' }}>
                  <PersonIcon />
                </ListItemIcon>
                {!isCompact && <ListItemText primary={"Accounts"} />}
              </ListItemButton>
            </Tooltip>
          </ListItem>
          <ListItem key={"groups"} disablePadding>
            <Tooltip title={isCompact ? 'Groups' : ''} placement="right">
              <ListItemButton
                onClick={() => {props.onNavigate({page: "Groups"})}}
                sx={{ justifyContent: isCompact ? 'center' : 'flex-start', px: 1.5 }}
              >
                <ListItemIcon sx={{ minWidth: 0, mr: isCompact ? 0 : 1.5, justifyContent: 'center' }}>
                  <AllInboxIcon />
                </ListItemIcon>
                {!isCompact && <ListItemText primary={"Groups"} />}
              </ListItemButton>
            </Tooltip>
          </ListItem>
        </List>
        <Divider />
        <Box
          sx={{
            width: '100%',
            height: 'calc(100vh - 180px)',
            bgcolor: 'background.paper',
            overflowY: 'auto',
            overflowX: 'hidden',
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
            '&::-webkit-scrollbar': { display: 'none' },
          }}
        >
          {!isCompact && <ListItem><ListItemText primary={"Submissions"}/></ListItem>}
          <List disablePadding>
            {groups.map((group) => (
              <ListItem key={group.id} disablePadding>
                <Tooltip title={isCompact ? group.name : ''} placement="right">
                  <ListItemButton
                    onClick={() => {
                      props.onNavigate({
                        page: "Submissions",
                        submissionGroup: group.id
                      });
                    }}
                    sx={{ justifyContent: isCompact ? 'center' : 'flex-start', px: 1.5 }}
                  >
                    <ListItemIcon sx={{ minWidth: 0, mr: isCompact ? 0 : 1.5, justifyContent: 'center' }}>
                      <AllInboxIcon fontSize="small" />
                    </ListItemIcon>
                    {!isCompact && <ListItemText primary={group.name} />}
                  </ListItemButton>
                </Tooltip>
              </ListItem>
            ))}
          </List>
        </Box>
        <Divider />
      </Drawer>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          p: 3,
          width: `calc(100% - ${activeDrawerWidth}px)`,
          minWidth: 0,
          overflowX: 'hidden',
        }}
      >
        <Toolbar />
        {props.children}
      </Box>
    </>
  );
}
