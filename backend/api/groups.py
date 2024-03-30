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
    from backend.database.models import PublicationGroup
except ImportError:
    from database.models import PublicationGroup


router = APIRouter(prefix="/groups")

@router.get("/")
async def get_all_groups() -> list[PublicationGroup]:
    """Get the List of all User Publication Groups."""
    return await PublicationGroup.all()

@router.put("/")
async def create_new_group(new_group: PublicationGroup) -> int:
    """Create a New Publication Group from the Required Data."""
    return await new_group.insert()
