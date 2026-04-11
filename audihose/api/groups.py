################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from fastapi import APIRouter, Body, HTTPException, Query, status
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


router = APIRouter(prefix="/groups")


def get_group_or_404(session, group_id: str) -> PublicationGroup:
    """Load a Group or Raise a 404 Error."""
    group = session.exec(
        select(PublicationGroup)
        .where(PublicationGroup.id == group_id)
        .options(selectinload(PublicationGroup.accounts))
    ).first()
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found.",
        )
    return group


def get_account_or_404(session, account_id: str) -> Account:
    """Load an Account or Raise a 404 Error."""
    account = session.exec(
        select(Account).where(Account.id == account_id)
    ).first()
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found.",
        )
    return account

@router.get("/")
def get_all_groups(session: SessionDependency) -> list[PublicationGroupSummary]:
    """Get the List of all User Publication Groups."""
    groups = session.exec(
        select(PublicationGroup).order_by(PublicationGroup.name)
    ).all()
    return [to_group_summary(group) for group in groups]

@router.get("/{group_id}")
def get_group_by_id(
    group_id: str,
    session: SessionDependency,
) -> PublicationGroupSummary:
    """Get the Publication Group by ID."""
    return to_group_summary(get_group_or_404(session=session, group_id=group_id))

@router.put("/")
def create_new_group(
    new_group: PublicationGroupCreate,
    session: SessionDependency,
) -> str:
    """Create a New Publication Group from the Required Data."""
    group = PublicationGroup(
        name=new_group.name,
        accepting_submissions=new_group.accepting_submissions,
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    return group.id

@router.patch("/")
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

@router.get("/by-account/{account_id}")
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

@router.get("/accounts/{group_id}")
def get_accounts_in_group(
    group_id: str,
    session: SessionDependency,
) -> list[AccountSummary]:
    """Get the Accounts Listed for a Publication Group."""
    group = get_group_or_404(session=session, group_id=group_id)
    return [to_account_summary(account) for account in group.accounts]

@router.put("/accounts/{group_id}")
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

@router.post("/accounts/{group_id}")
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

@router.patch("/accounts/{group_id}")
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

@router.delete("/accounts/{group_id}")
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
