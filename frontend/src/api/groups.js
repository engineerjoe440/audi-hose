
import { api_client, fetchToken } from '../auth';

  
export const getGroupsList = (props) => {
    api_client.get("groups", {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${fetchToken()}`
      },
    }).then(res => res.data).then(jsonData => {
      // Record the Groups
      console.log(jsonData);
      props.onSet(jsonData);
    })
    .catch((error) => {
      if( error.response ){
        console.log(error.response.data); // => the response payload
      }
    });
  }

export const getGroupsListByAccount = (props) => {
    if (!props.accountId) {
      return
    }
    api_client.get(`groups/by-account/${props.accountId}`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${fetchToken()}`
      },
    }).then(res => res.data).then(jsonData => {
      // Record the Groups for This Account
      props.onSet(jsonData);
    })
    .catch((error) => {
      if( error.response ){
        console.log(error.response.data); // => the response payload
      }
    });
  }