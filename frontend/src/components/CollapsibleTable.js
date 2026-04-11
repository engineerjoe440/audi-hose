import * as React from 'react';
import PropTypes from 'prop-types';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import Fab from '@mui/material/Fab';
import IconButton from '@mui/material/IconButton';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';
import toast from 'react-hot-toast';
import { SelectGroupDialog } from './AdminViews/AdminDialog';
import { api_client, fetchToken } from '../auth';


export function CollapsibleTableRow(props) {
  const { row } = props;
  const [groupsDrawerOpen, setGroupsDrawerOpen] = React.useState(false);
  const [dialogOpen, setDialogOpen] = React.useState(false);

  const doRemoveAccount = () => {
    api_client.delete("accounts",
      {
        data: row,
        withCredentials: true,
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${fetchToken()}`
        },
      }
    ).then(res => res.data).then(jsonData => {
      toast.custom(
        <Paper elevation={6}>
          <Typography variant="h5">
            Account Successfully Removed
          </Typography>
          <Button
            color="inherit"
            endIcon={<RefreshIcon />}
            onClick={() => {window.location.reload()}}
          >
            Refresh
          </Button>
        </Paper>,
        { duration: 8000 }
      );
    })
    .catch((error) => {
      if( error.response ){
        console.log(error.response.data);
      }
    });
  }

  const doRemoveGroup = (groupId) => {
    api_client.delete(`groups/accounts/${groupId}`,
      {
        withCredentials: true,
        params: {
          account_id: row.id,
        },
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${fetchToken()}`
        },
      }
    ).then(res => res.data).then(jsonData => {
      toast.custom(
        <Paper elevation={6}>
          <Typography variant="h5">
            Group Successfully Removed
          </Typography>
          <Button
            color="inherit"
            endIcon={<RefreshIcon />}
            onClick={() => {window.location.reload()}}
          >
            Refresh
          </Button>
        </Paper>,
        { duration: 8000 }
      );
    })
    .catch((error) => {
      if( error.response ){
        console.log(error.response.data);
      }
    });
  }

  return (
    <React.Fragment>
      <SelectGroupDialog
        open={dialogOpen}
        account={row}
        onClose={() => {setDialogOpen(false)}}
      />

      {/* Right-side groups drawer */}
      <Drawer
        anchor="right"
        open={groupsDrawerOpen}
        onClose={() => setGroupsDrawerOpen(false)}
      >
        <Box sx={{ width: 320 }} role="presentation">
          <Toolbar sx={{ justifyContent: 'space-between' }}>
            <Typography variant="h6" noWrap>
              Groups — {row.name}
            </Typography>
            <IconButton
              aria-label="close"
              onClick={() => setGroupsDrawerOpen(false)}
            >
              <CloseIcon />
            </IconButton>
          </Toolbar>
          <Divider />
          <Box sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle1">Assigned Groups</Typography>
              <Fab
                size="small"
                color="primary"
                aria-label="add group"
                onClick={() => setDialogOpen(true)}
              >
                <AddIcon />
              </Fab>
            </Box>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {!!row.associations && row.associations.map((associationRow) => (
                  <TableRow key={associationRow.id}>
                    <TableCell component="th" scope="row">
                      {associationRow.name}
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => doRemoveGroup(associationRow.id)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
        </Box>
      </Drawer>

      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell component="th" scope="row">
          {row.name}
        </TableCell>
        <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>
          {row.email}
        </TableCell>
        <TableCell align="right">
          <Button
            size="small"
            variant="contained"
            sx={{ mr: 1 }}
            onClick={() => setGroupsDrawerOpen(true)}
          >
            Edit Groups
          </Button>
          <IconButton onClick={doRemoveAccount}>
            <DeleteIcon />
          </IconButton>
        </TableCell>
      </TableRow>
    </React.Fragment>
  );
}

CollapsibleTableRow.propTypes = {
  row: PropTypes.shape({
    associations: PropTypes.arrayOf(
      PropTypes.shape({
        name: PropTypes.string.isRequired,
        id: PropTypes.string.isRequired,
      }),
    ).isRequired,
    name: PropTypes.string.isRequired,
    email: PropTypes.string.isRequired,
    id: PropTypes.string.isRequired,
  }).isRequired,
};

export function CollapsibleTable({
    childRows, // the rows which can be displayed
  }) {
    return (
      <TableContainer component={Paper}>
        <Table aria-label="collapsible table" size="small">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell sx={{ display: { xs: 'none', sm: 'table-cell' } }}>Email</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {!!childRows && childRows.map((row) => (
              <CollapsibleTableRow key={row.name} row={row} />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
  }
