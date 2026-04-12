################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from fastapi import Header, HTTPException, status

from ..database import Account, PublicationGroup
from ..security import verify_token


def require_api_auth(authorization: str | None = Header(default=None)) -> str:
    """Simple bearer-token check for API endpoints."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    token = authorization.split(" ", 1)[1].strip()
    if not token or not verify_token(token=token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token


def get_account_or_404(session, account_id: str) -> Account:
    """Load an Account or raise a 404 error."""
    account = session.get(Account, account_id)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found.",
        )
    return account


def get_group_or_404(session, group_id: str) -> PublicationGroup:
    """Load a PublicationGroup or raise a 404 error."""
    group = session.get(PublicationGroup, group_id)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )
    return group
