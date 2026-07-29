################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from ..database import Account, SessionDependency, to_account_summary
from ..security import decode_jwt, verify_token
from . import accounts, groups, recordings
from .common import require_api_auth

router = APIRouter(prefix="/api/v1")

router.include_router(accounts.router)
router.include_router(groups.router)
router.include_router(recordings.router)


@router.get("/my-account")
def get_my_account_compat(
    session: SessionDependency,
    token: Annotated[str | None, Query()] = None,
    authorization: str | None = Header(default=None),
):
    """Compatibility endpoint for current account lookup."""
    bearer_token = None
    if authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        bearer_token = authorization.split(" ", 1)[1].strip()
    selected_token = token or bearer_token
    if not selected_token or not verify_token(token=selected_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    payload = decode_jwt(selected_token) or {}
    account_id = payload.get("id") or payload.get("account_id")
    if not account_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    account = session.get(Account, account_id)
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return to_account_summary(account)


@router.get("/accounts/{account_id}/groups", dependencies=[Depends(require_api_auth)])
def get_groups_for_account_compat(account_id: str, session: SessionDependency):
    """Compatibility alias for account group listing."""
    return groups.get_groups_for_account(account_id=account_id, session=session)


@router.get("/groups/{group_id}/recordings", dependencies=[Depends(require_api_auth)])
def get_recordings_by_group_compat(group_id: str, session: SessionDependency):
    """Compatibility alias for group recordings listing."""
    return recordings.get_recordings_by_group(group_id=group_id, session=session)
