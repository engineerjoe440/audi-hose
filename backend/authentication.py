################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from typing import Annotated, Union

from fastapi import (
    Request, APIRouter, HTTPException, status, Query, Cookie, Depends
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from loguru import logger

try:
    from backend.sessions import get_session, close_session
    from backend.database.models import Account, Login, NewAccountData
    from backend.security import verify_token, check_password, sign_jwt
    from backend.api.accounts import create_new_account
except ImportError:
    from sessions import get_session, close_session
    from database.models import Account, Login, NewAccountData
    from api.accounts import create_new_account
    from security import verify_token, check_password, sign_jwt


router = APIRouter()


class LoginItem(BaseModel):
    """Login Parameters."""
    email: str
    password: str
    client_token: str

class TokenResponse(BaseModel):
    """JSON Web Token Response for Authentication."""
    token: Union[str, None] = None
    message: Union[str, None] = None


async def get_query_token(
    token: Annotated[str | None, Query()] = None,
):
    """Get the Client Token from a Query."""
    if token is None or not verify_token(token=token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token


# Define the Authentication Bearer System
class JWTBearer(HTTPBearer):
    """Uploader Authentication Validator"""
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, req: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(req)
        if credentials:
            if not credentials.scheme == "Bearer":
                logger.warning("Invalid authentication scheme.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                logger.warning("Invalid token or expired token.")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token or expired token."
                )
            if (session := get_session(credentials.credentials)):
                logger.warning("Session Expired.")
                if not session:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Session Expired."
                    )
            return credentials.credentials
        # Otherwise
        logger.warning("Invalid authorization code.")
        raise HTTPException(
            status_code=403,
            detail="Invalid authorization code."
        )

    def verify_jwt(self, jwt_token: str) -> bool:
        """Verify that the JWT is Appropriately Signed."""
        return verify_token(token=jwt_token)


@router.post("/login", response_model=TokenResponse)
async def user_login(login_item: LoginItem) -> TokenResponse:
    """Authenticate admin user and provide a JSON Web Token."""
    session = get_session(client_token=login_item.client_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="could not identify active session object, please reload",
        )

    data = jsonable_encoder(login_item)
    email = data["email"]
    password = data["password"]

    response = TokenResponse(message="Invalid Credentials.")

    try:
        # Obtain the Account Corresponding to the User Email
        accounts = await Account.filter(email=email)
        if accounts:
            # Verify Password
            for account in accounts:
                if account.id is None:
                    continue
                login_db_entry = await Login.get(id=account.id)
                if check_password(password, login_db_entry.hashed_password):
                    # Validated Account - Sign Token
                    response.token = sign_jwt({
                        "email": email,
                        "id": account.id,
                        "session": session.client_token,
                    })
                    response.message = None
                    # Set Session Parameters
                    session.email = email
                    session.account_id = account.id
    except ValueError as err:
        response.message = (
            f"Server failure: '{err}'\n"
            "If this issue persists, contact administrator."
        )
        logger.exception(err)
    return response

@router.post(
    "/refresh-token",
    dependencies=[Depends(JWTBearer())],
    response_model=TokenResponse
)
async def refresh_token(
    client_token: Annotated[str | None, Cookie()] = None
) -> TokenResponse:
    """Refresh the JSON Web Token for an Authenticated admin User."""
    token = TokenResponse()
    if client_token:
        session = get_session(client_token=client_token)
        if session:
            token.token = sign_jwt({
                "email": session.email,
                "id": session.account_id,
                "session": session.client_token,
            })
    return token

@router.post("/logout", dependencies=[Depends(JWTBearer())])
async def logout(client_token: Annotated[str | None, Cookie()] = None):
    """Log Active User Out of System."""
    if client_token:
        close_session(client_token=client_token)

@router.get("/signup-required")
async def determine_signup_status() -> bool:
    """Determine Whether a User Must be Created, First."""
    return (await Account.count()) == 0

@router.post("/create-initial-account")
async def create_initial_account(
    initial_account_data: NewAccountData,
    client_token: Annotated[str | None, Cookie()] = None
) -> TokenResponse:
    """Create the Very First Account."""
    if await determine_signup_status():
        account_id = await create_new_account(account_data=initial_account_data)
        token = TokenResponse()
        session = get_session(client_token=client_token)
        token.token = sign_jwt({
            "email": initial_account_data.email,
            "id": account_id,
            "session": client_token,
        })
        session.email = initial_account_data.email
        session.account_id = account_id
        return token
    raise HTTPException(
        status_code=status.HTTP_423_LOCKED,
        detail="Cannot create a new account."
    )
