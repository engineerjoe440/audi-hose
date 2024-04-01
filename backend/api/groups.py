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


router = APIRouter(prefix="/groups")

@router.get("/")
async def get_all_groups() -> list[PublicationGroup]:
    """Get the List of all User Publication Groups."""
    return await PublicationGroup.all()

@router.put("/")
async def create_new_group(new_group: PublicationGroup) -> int:
    """Create a New Publication Group from the Required Data."""
    return await new_group.insert()

@router.post("/")
async def modify_existing_group(group: PublicationGroup) -> int:
    """Modify an Existing Publication Group Using the Supplied Data."""
    return await group.update()

@router.get("/by-account/{account_id}")
async def get_groups_for_account(account_id: str) -> list[PublicationGroup]:
    """Get the List of Groups Associated with an Account."""
    account = await Account.get(id=account_id)
    groups = []
    for group in await PublicationGroup.all():
        if account in group.accounts:
            groups.append(group)
    return groups

@router.get("/accounts/{group_id}")
async def get_accounts_in_group(group_id: str) -> list[Account]:
    """Get the Accounts Listed for a Publication Group."""
    return (await PublicationGroup.get(id=group_id)).accounts

@router.put("/accounts/{group_id}")
async def add_account_to_group(
    group_id: str,
    account: Account
):
    """Add an Account to a Publication Group."""
    group = await PublicationGroup.get(id=group_id)
    group.accounts.append(account)
    await group.update()

@router.patch("/accounts/{group_id}")
async def add_account_id_to_group(
    group_id: str,
    account_id: str,
):
    """Add an Account to a Publication Group."""
    group = await PublicationGroup.get(id=group_id)
    account = await Account.get(id=account_id)
    group.accounts.append(account)
    await group.update()

@router.post("/accounts/{group_id}")
async def modify_accounts_in_group(
    group_id: str,
    accounts: list[Account],
):
    """Add an Account to a Publication Group."""
    group = await PublicationGroup.get(id=group_id)
    group.accounts = accounts
    await group.update()

@router.delete("/accounts/{group_id}")
async def remove_account_from_group(
    group_id: str,
    account_id: str
):
    """Remove an Account from a Publication Group."""
    group = await PublicationGroup.get(id=group_id)
    del group.accounts[group.accounts.index(account_id)]
    await group.update()
