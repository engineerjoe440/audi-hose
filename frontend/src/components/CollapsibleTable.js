import * as React from 'react';
import PropTypes from 'prop-types';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Collapse from '@mui/material/Collapse';
import IconButton from '@mui/material/IconButton';
import Fab from '@mui/material/Fab';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import AddIcon from '@mui/icons-material/Add';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';
import toast from 'react-hot-toast';
import { api_client, fetchToken } from '../auth';


export function CollapsibleTableRow(props) {
  const { row } = props;
  const [open, setOpen] = React.useState(false);

  const doRemove = () => {
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
      // Account Has Been Removed
      toast.custom(
        <Paper elevation={6}>
          <Typography variant="h5">
            Account Successfully Removed
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
  }

  return (
    <React.Fragment>
      <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
        <TableCell>
          <IconButton
            aria-label="expand row"
            size="small"
            onClick={() => setOpen(!open)}
          >
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell component="th" scope="row">
          {row.name}
        </TableCell>
        <TableCell component="th" scope="row">
          {row.email}
        </TableCell>
        <TableCell>{row.id}</TableCell>
        <TableCell align="right">
          <IconButton onClick={doRemove}>
            <DeleteIcon/>
          </IconButton>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Grid container>
                <Grid item xs={10}>
                  <Typography variant="h6" gutterBottom component="div">
                    Groups
                  </Typography>
                </Grid>
                <Grid item xs={2}>
                  <Box sx={{ '& > :not(style)': { m: 1 } }}>
                    <Fab size="small" color="primary" aria-label="add">
                      <AddIcon />
                    </Fab>
                  </Box>
                </Grid>
              </Grid>
              <Table size="small" aria-label="purchases">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell align="right">ID</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {!!row.associations && row.associations.map((associationRow) => (
                    <TableRow key={associationRow.id}>
                      <TableCell component="th" scope="row">
                        {associationRow.name}
                      </TableCell>
                      <TableCell align="right">{row.id}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </Collapse>
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
              <TableCell />
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>ID</TableCell>
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
