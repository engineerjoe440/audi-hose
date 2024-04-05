import * as React from 'react';
import { Box, Typography, Fab, Grid } from '@mui/material';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import AddIcon from '@mui/icons-material/Add';
import { NewGroupDialog } from './AdminDialog';
import { getGroupsList } from '../api/groups';


export function AdminGroupsView() {
    const [groups, setGroups] = React.useState([]);
    const [open, setOpen] = React.useState(false);
  
    React.useEffect(()=>{
      // Load Requisites when page Completes
      getGroupsList({onSet: setGroups});
    },[]);

  return (
    <>
      <NewGroupDialog open={open} onClose={() => {setOpen(false)}} />
      <Grid container>
        <Grid item xs={10}>
          <Typography variant='h3'>Submission Groups</Typography>
        </Grid>
        <Grid item xs={2}>
          <Box sx={{ '& > :not(style)': { m: 1 } }}>
            <Fab color="primary" aria-label="add" onClick={() => {setOpen(true)}}>
              <AddIcon />
            </Fab>
          </Box>
        </Grid>
      </Grid>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>ID</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {groups.map((row) => (
              <TableRow
                key={row.name}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {row.name}
                </TableCell>
                <TableCell>{row.id}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
}
