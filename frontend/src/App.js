/* Admin Landing Page. */
import * as React from 'react';
import { useSearchParams } from "react-router-dom";
import AppBase from './components/AppBase';
import { AdminAccountsView } from './components/AdminViews/AdminAccountsView';
import { AdminGroupsView } from './components/AdminViews/AdminGroupsView';
import { AdminSubmissionGroup } from './components/AdminViews/AdminSubmissionGroup';

export default function AdminApp() {
  let [searchParams, setSearchParams] = useSearchParams({page: "Accounts"});

  React.useEffect(()=>{
    // Load Requisites when page Completes
  },[]);

  const navigate = (navParams) => {
    setSearchParams(navParams)
  }

  return (
    <AppBase bannerTitle="Audi-Hose" onNavigate={navigate} >
      {searchParams.get("page") === "Accounts" && <AdminAccountsView />}
      {searchParams.get("page") === "Groups" && <AdminGroupsView />}
      {searchParams.get("page") === "Submissions" &&
        <AdminSubmissionGroup group={searchParams.get("submissionGroup")} />}
    </AppBase>
  );
}

