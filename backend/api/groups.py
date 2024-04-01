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
    from backend.database.models import PublicationGroup, Account
except ImportError:
    from database.models import PublicationGroup, Account


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

@router.patch("/{group_id}")
async def add_user_ids_to_group(
    group_id: str,
    new_user_ids: list[str],
) -> int:
    """Add New Users to a Publication Group by ID."""
    group = await PublicationGroup.get(id=group_id)
    added_count = 0
    for new_id in new_user_ids:
        new_user = await Account.get(id=new_id)
        if new_user not in group.accounts:
            group.accounts.append(new_user)
            added_count += 1
    return added_count
