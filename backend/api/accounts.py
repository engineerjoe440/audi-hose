################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from typing import Annotated

from fastapi import APIRouter, Cookie

try:
    from backend.database.models import (
        Account, AccountWithGroups, Login, NewAccountData, PublicationGroup
    )
    from backend.security import get_hashed_password
    from backend.sessions import get_session
except ImportError:
    from database.models import (
        Account, AccountWithGroups, Login, NewAccountData, PublicationGroup
    )
    from security import get_hashed_password
    from sessions import get_session


router = APIRouter(prefix="/accounts")


@router.get("/")
async def get_all_accounts() -> list[Account]:
    """Get the List of all User Accounts."""
    return await Account.all()

@router.get("/me")
async def get_my_account(
    client_token: Annotated[str | None, Cookie()] = None,
) -> Account:
    """Get the List of all User Accounts."""
    session = get_session(client_token=client_token)
    if session:
        return await Account.get(id=session.account_id)

@router.get("/with-groups")
async def get_accounts_with_associations() -> list[AccountWithGroups]:
    """Get List of Accounts with Group Information."""
    accounts_list = []
    for account in await Account.all():
        groups = []
        for group in await PublicationGroup.all():
            if account in group.accounts:
                groups.append(group)
        accounts_list.append(AccountWithGroups(
            id=account.id,
            name=account.name,
            email=account.email,
            associations=groups,
        ))
    return accounts_list

@router.put("/")
async def create_new_account(account_data: NewAccountData) -> str:
    """Create a New Account from the Required Data."""
    new_account = await Account.create(
        name=account_data.name,
        email=account_data.email,
    )
    await Login.create(
        id=new_account.id,
        hashed_password=get_hashed_password(account_data.password),
    )
    return new_account.id

@router.delete("/")
async def delete_acount(account: Account) -> int:
    """Delete an Account."""
    await (await Login.get(id=account.id)).delete()
    return await account.delete()

@router.delete("/{account_id}")
async def delete_acount_by_id(account_id: str) -> int:
    """Delete an Account Using Only its ID."""
    await (await Login.get(id=account_id)).delete()
    return await (await Account.get(id=account_id)).delete()
