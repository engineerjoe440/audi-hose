/* Admin Landing Page. */
import * as React from 'react';
import { useSearchParams } from "react-router-dom";
import AppBase from './components/AppBase';
import { AdminAccountsView } from './components/AdminAccountsView';
import { AdminGroupsView } from './components/AdminGroupsView';

export default function AdminApp() {
  let [searchParams, setSearchParams] = useSearchParams({page: "Accounts"});

  React.useEffect(()=>{
    // Load Requisites when page Completes
  },[]);

  const navigate = (pageName) => {
    setSearchParams({page: pageName})
  }

  return (
    <AppBase bannerTitle="Audi-Hose" onNavigate={navigate} >
      {searchParams.get("page") === "Accounts" && <AdminAccountsView />}
      {searchParams.get("page") === "Groups" && <AdminGroupsView />}
    </AppBase>
  );
}

