################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import select

from ..database import (
    Account,
    AccountSummary,
    AccountWithGroups,
    Login,
    NewAccountData,
    SessionDependency,
    to_account_summary,
    to_account_with_groups,
)
from ..security import get_hashed_password
from ..sessions import get_session as get_user_session


router = APIRouter(prefix="/accounts")


def create_account(session, account_data: NewAccountData) -> str:
    """Create an Account and its Associated Login Record."""
    new_account = Account(name=account_data.name, email=account_data.email)
    session.add(new_account)
    session.flush()
    session.add(
        Login(
            id=new_account.id,
            hashed_password=get_hashed_password(account_data.password),
        )
    )
    session.commit()
    session.refresh(new_account)
    return new_account.id


def delete_account(session, account_id: str) -> int:
    """Delete an Account and its Associated Login Record."""
    login = session.get(Login, account_id)
    account = session.get(Account, account_id)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found.",
        )
    if login is not None:
        session.delete(login)
    session.delete(account)
    session.commit()
    return 1


@router.get("/")
def get_all_accounts(session: SessionDependency) -> list[AccountSummary]:
    """Get the List of all User Accounts."""
    accounts = session.exec(select(Account).order_by(Account.name)).all()
    return [to_account_summary(account) for account in accounts]

@router.get("/me")
def get_my_account(
    session: SessionDependency,
    client_token: Annotated[str | None, Cookie()] = None,
) -> AccountSummary | None:
    """Get the List of all User Accounts."""
    user_session = get_user_session(client_token=client_token)
    if user_session and user_session.account_id:
        account = session.get(Account, user_session.account_id)
        if account is not None:
            return to_account_summary(account)
    return None

@router.get("/with-groups")
def get_accounts_with_associations(
    session: SessionDependency,
) -> list[AccountWithGroups]:
    """Get List of Accounts with Group Information."""
    accounts = session.exec(
        select(Account)
        .options(selectinload(Account.groups))
        .order_by(Account.name)
    ).all()
    return [to_account_with_groups(account) for account in accounts]

@router.put("/")
def create_new_account(
    session: SessionDependency,
    account_data: NewAccountData,
) -> str:
    """Create a New Account from the Required Data."""
    return create_account(session=session, account_data=account_data)

@router.delete("/")
def delete_acount(account: AccountSummary, session: SessionDependency) -> int:
    """Delete an Account."""
    return delete_account(session=session, account_id=account.id)

@router.delete("/{account_id}")
def delete_acount_by_id(account_id: str, session: SessionDependency) -> int:
    """Delete an Account Using Only its ID."""
    return delete_account(session=session, account_id=account_id)
