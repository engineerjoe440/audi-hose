################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import selectinload
from sqlmodel import select

from ..database import (
    Account,
    AccountMembershipUpdate,
    AccountSummary,
    PublicationGroup,
    PublicationGroupCreate,
    PublicationGroupSummary,
    PublicationGroupUpdate,
    SessionDependency,
    to_account_summary,
    to_group_summary,
)
from .common import get_account_or_404, get_group_or_404, require_api_auth

router = APIRouter(prefix="/groups")


@router.get("/", dependencies=[Depends(require_api_auth)])
def get_all_groups(session: SessionDependency) -> list[PublicationGroupSummary]:
    """Get the List of all User Publication Groups."""
    groups = session.exec(
        select(PublicationGroup).order_by(PublicationGroup.name)
    ).all()
    return [to_group_summary(group) for group in groups]

@router.get("/{group_id}", dependencies=[Depends(require_api_auth)])
def get_group_by_id(
    group_id: str,
    session: SessionDependency,
) -> PublicationGroupSummary:
    """Get the Publication Group by ID."""
    return to_group_summary(get_group_or_404(session=session, group_id=group_id))

@router.put("/", dependencies=[Depends(require_api_auth)])
def create_new_group(
    new_group: PublicationGroupCreate,
    session: SessionDependency,
) -> PublicationGroupSummary:
    """Create a New Publication Group from the Required Data."""
    group = PublicationGroup(
        name=new_group.name,
        accepting_submissions=new_group.accepting_submissions,
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    return to_group_summary(group)

@router.patch("/", dependencies=[Depends(require_api_auth)])
def modify_existing_group(
    group: PublicationGroupUpdate,
    session: SessionDependency,
) -> int:
    """Modify an Existing Publication Group Using the Supplied Data."""
    current_group = get_group_or_404(session=session, group_id=group.id)
    current_group.name = group.name
    current_group.accepting_submissions = group.accepting_submissions
    session.add(current_group)
    session.commit()
    return 1

@router.get("/by-account/{account_id}", dependencies=[Depends(require_api_auth)])
def get_groups_for_account(
    account_id: str,
    session: SessionDependency,
) -> list[PublicationGroupSummary]:
    """Get the List of Groups Associated with an Account."""
    account = session.exec(
        select(Account)
        .where(Account.id == account_id)
        .options(selectinload(Account.groups))
    ).first()
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found.",
        )
    return [to_group_summary(group) for group in account.groups]

@router.get("/accounts/{group_id}", dependencies=[Depends(require_api_auth)])
@router.get("/{group_id}/accounts", dependencies=[Depends(require_api_auth)])
def get_accounts_in_group(
    group_id: str,
    session: SessionDependency,
) -> list[AccountSummary]:
    """Get the Accounts Listed for a Publication Group."""
    group = get_group_or_404(session=session, group_id=group_id)
    return [to_account_summary(account) for account in group.accounts]

@router.put("/accounts/{group_id}", dependencies=[Depends(require_api_auth)])
def add_account_to_group(
    group_id: str,
    account: AccountSummary,
    session: SessionDependency,
):
    """Add an Account to a Publication Group."""
    group = get_group_or_404(session=session, group_id=group_id)
    selected_account = get_account_or_404(session=session, account_id=account.id)
    if not any(existing_account.id == selected_account.id for existing_account in group.accounts):
        group.accounts.append(selected_account)
        session.add(group)
        session.commit()
    return 1

@router.post("/accounts/{group_id}", dependencies=[Depends(require_api_auth)])
def add_account_id_to_group(
    group_id: str,
    session: SessionDependency,
    account_id: str = Query(...),
):
    """Add an Account to a Publication Group."""
    group = get_group_or_404(session=session, group_id=group_id)
    selected_account = get_account_or_404(session=session, account_id=account_id)
    if not any(existing_account.id == selected_account.id for existing_account in group.accounts):
        group.accounts.append(selected_account)
        session.add(group)
        session.commit()
    return 1

@router.patch("/accounts/{group_id}", dependencies=[Depends(require_api_auth)])
def modify_accounts_in_group(
    group_id: str,
    session: SessionDependency,
    accounts: AccountMembershipUpdate = Body(...),
):
    """Add an Account to a Publication Group."""
    group = get_group_or_404(session=session, group_id=group_id)
    group.accounts = [
        get_account_or_404(session=session, account_id=account_id)
        for account_id in accounts.account_ids
    ]
    session.add(group)
    session.commit()
    return 1

@router.delete("/accounts/{group_id}", dependencies=[Depends(require_api_auth)])
def remove_account_from_group(
    group_id: str,
    account_id: str,
    session: SessionDependency,
):
    """Remove an Account from a Publication Group."""
    group = get_group_or_404(session=session, group_id=group_id)
    group.accounts = [
        account for account in group.accounts if account.id != account_id
    ]
    session.add(group)
    session.commit()
    return 1


@router.patch("/{group_id}", dependencies=[Depends(require_api_auth)])
def modify_existing_group_by_id(
    group_id: str,
    group: PublicationGroupCreate,
    session: SessionDependency,
) -> PublicationGroupSummary:
    """Compatibility endpoint for patching group by path ID."""
    current_group = get_group_or_404(session=session, group_id=group_id)
    current_group.name = group.name
    current_group.accepting_submissions = group.accepting_submissions
    session.add(current_group)
    session.commit()
    session.refresh(current_group)
    return to_group_summary(current_group)


@router.post("/{group_id}/accounts", dependencies=[Depends(require_api_auth)])
def add_account_id_to_group_body(
    group_id: str,
    session: SessionDependency,
    payload: dict = Body(...),
):
    """Compatibility endpoint for adding account to a group via JSON payload."""
    account_id = payload.get("account_id")
    if not account_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    group = get_group_or_404(session=session, group_id=group_id)
    selected_account = get_account_or_404(session=session, account_id=account_id)
    if not any(existing_account.id == selected_account.id for existing_account in group.accounts):
        group.accounts.append(selected_account)
        session.add(group)
        session.commit()
    return [to_account_summary(account) for account in group.accounts]


@router.put("/{group_id}/accounts", dependencies=[Depends(require_api_auth)])
def replace_accounts_in_group(
    group_id: str,
    accounts: AccountMembershipUpdate,
    session: SessionDependency,
):
    """Compatibility endpoint for replacing group membership via PUT."""
    group = get_group_or_404(session=session, group_id=group_id)
    group.accounts = [
        get_account_or_404(session=session, account_id=account_id)
        for account_id in accounts.account_ids
    ]
    session.add(group)
    session.commit()
    return [to_account_summary(account) for account in group.accounts]
