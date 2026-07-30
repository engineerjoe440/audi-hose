################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from fastapi import APIRouter, Depends
from sqlmodel import select

from ..database import (
    Publisher,
    SessionDependency,
    to_publisher_read,
)
from .common import require_api_auth

router = APIRouter(prefix="/publishers")

@router.get("/", dependencies=[Depends(require_api_auth)])
def get_all_publishers(session: SessionDependency) -> list[Publisher]:
    """Get the List of all Publishers."""
    publishers = session.exec(
        # pylint: disable-next=E1101
        select(Publisher).order_by(Publisher.name.asc()) #noqa: E1101
    ).all()
    return [to_publisher_read(publisher) for publisher in publishers]
