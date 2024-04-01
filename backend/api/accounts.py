################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from fastapi import APIRouter

try:
    from backend.database.models import Account, PublicationGroup
except ImportError:
    from database.models import Account, PublicationGroup


router = APIRouter(prefix="/accounts")

@router.get("/")
async def get_all_accounts() -> list[Account]:
    """Get the List of all User Accounts."""
    return await Account.all()

@router.put("/")
async def create_new_account(new_account: Account) -> int:
    """Create a New Account from the Required Data."""
    return await new_account.insert()

@router.delete("/")
async def delete_acount(account: Account) -> int:
    """Delete an Account."""
    return await account.delete()

@router.delete("/{account_id}")
async def delete_acount_by_id(account_id: str) -> int:
    """Delete an Account Using Only its ID."""
    return await (await Account.get(id=account_id)).delete()

@router.get("/{account_id}/groups")
async def get_account_groups(account_id: str) -> list[PublicationGroup]:
    """Get the List of Publication Groups for the Account."""
    account = await Account.get(id=account_id)
    return await PublicationGroup.filter(accounts=Contains(account))
