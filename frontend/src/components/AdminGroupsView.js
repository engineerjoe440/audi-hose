import * as React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import { api_client, fetchToken } from '../auth';


export function AdminGroupsView() {
    const [groups, setGroups] = React.useState([]);
  
    React.useEffect(()=>{
      // Load Requisites when page Completes
      getGroupsList();
    },[]);
  
    const getGroupsList = () => {
      api_client.get("groups", {
        withCredentials: true,
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${fetchToken()}`
        },
      }).then(res => res.data).then(jsonData => {
        // Record the Groups
        setGroups(jsonData);
      })
      .catch((error) => {
        if( error.response ){
          console.log(error.response.data); // => the response payload
        }
      });
    }

  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} size="small">
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell align="right">ID</TableCell>
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
              <TableCell align="right">{row.id}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
