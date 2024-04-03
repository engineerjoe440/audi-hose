################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from typing import Annotated

from fastapi import APIRouter, Cookie
from pydantic import BaseModel, EmailStr

try:
    from backend.database.models import Account
    from backend.authentication import get_hashed_password
    from backend.sessions import get_session
except ImportError:
    from database.models import Account
    from authentication import get_hashed_password
    from sessions import get_session


router = APIRouter(prefix="/accounts")

class NewAccountData(BaseModel):
    """Data Required for a New Account."""
    name: str
    email: EmailStr
    password: str

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

@router.put("/")
async def add_new_account(new_account: Account) -> int:
    """Create a New Account from the Provided Definition."""
    return await new_account.insert()

@router.put("/create")
async def create_new_account(account_data: NewAccountData) -> str:
    """Create a New Account from the Required Data."""
    new_account = await Account.create(
        name=account_data.name,
        email=account_data.email,
        hashed_password=get_hashed_password(account_data.password),
    )
    return new_account.id

@router.delete("/")
async def delete_acount(account: Account) -> int:
    """Delete an Account."""
    return await account.delete()

@router.delete("/{account_id}")
async def delete_acount_by_id(account_id: str) -> int:
    """Delete an Account Using Only its ID."""
    return await (await Account.get(id=account_id)).delete()
