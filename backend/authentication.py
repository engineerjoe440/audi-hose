################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from typing import Annotated, Union
import time
import secrets

import bcrypt
import jwt
from fastapi import (
    Request, APIRouter, HTTPException, status, Query, Cookie, Depends
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from loguru import logger

try:
    from backend.sessions import get_session, close_session, UserSession
    from backend.database import Account
except ImportError:
    from sessions import get_session, close_session, UserSession
    from database import Account

JWT_SECRET = secrets.token_urlsafe(24) # Reloaded each time app starts
JWT_ALGORITHM ="HS256"
JWT_EXPIRY_LENGTH = 1800 # 30 minutes


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


def get_hashed_password(plain_text_password: str) -> str:
    """Hash a password for the first time."""
    # (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(
        plain_text_password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode('utf-8')

def check_password(plain_text_password: str, hashed_password: str) -> bool:
    """Check hashed password."""
    # Using bcrypt the salt is saved into the hash itself
    return bcrypt.checkpw(
        plain_text_password.encode("utf-8"),
        hashed_password.encode("utf-8"))

def sign_jwt(payload: dict) -> dict[str, str]:
    """Generate a JSON Web Token (assuming valid authentication)."""
    payload["expires"] = time.time() + JWT_EXPIRY_LENGTH
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_jwt(token: str) -> dict:
    """Decode the JSON Web Token and Validate it."""
    try:
        decoded_token = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        if decoded_token["expires"] >= time.time():
            return decoded_token
        else:
            return None
    except jwt.exceptions.DecodeError:
        return {}

def verify_token(token: str) -> bool:
    """Verify that the token can be decoded, and that it's valid."""
    try:
        payload = decode_jwt(token)
        return bool(payload)
    except jwt.exceptions.DecodeError:
        return False


async def get_query_token(
    token: Annotated[str | None, Query()] = None,
):
    if token is None or not verify_token(token=token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token


# Define the Authentication Bearer System
class JWTBearer(HTTPBearer):
    """Uploader Authentication Validator"""
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer,
            self
        ).__call__(request)
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

async def perform_login(
    login: LoginItem,
    client_session: UserSession,
) -> TokenResponse:
    """Perform Authentication, Returning a Response with Token or Message."""
    data = jsonable_encoder(login)
    email = data["email"]
    password = data["password"]

    response = TokenResponse(message="Invalid Credentials.")

    try:
        # Obtain the Account Corresponding to the User Email
        accounts = await Account.filter(email=email)
        if accounts:
            # Verify Password
            for account in accounts:
                if check_password(password, account.hashed_password):
                    # Validated Account - Sign Token
                    response.token = sign_jwt({
                        "email": email,
                        "id": account.id,
                        "session": client_session.client_token,
                    })
                    response.message = None
    except ValueError as err:
        response.message = (
            f"Server failure: '{err}'\n"
            "If this issue persists, contact administrator."
        )
    return response

@router.post("/login", response_model=TokenResponse)
async def user_login(
    login_item: LoginItem,
    #request: Request
) -> TokenResponse:
    """Authenticate admin user and provide a JSON Web Token."""
    session = get_session(client_token=login_item.client_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="could not identify active session object, please reload",
        )
    return await perform_login(login=login_item, client_session=session)

@router.post(
    "/refresh-token",
    dependencies=[Depends(JWTBearer())],
    response_model=TokenResponse
)
async def refresh_token(
    client_token: Annotated[str | None, Cookie()] = None
) -> TokenResponse:
    """Refresh the JSON Web Token for an Authenticated admin User."""
    zsuite_email = "admin"
    if client_token:
        session = get_session(client_token=client_token)
        zsuite_email = session.zsuite_account_email
    token = TokenResponse()
    token.token = sign_jwt({"zsuite-email": zsuite_email})
    return token

@router.post("/logout", dependencies=[Depends(JWTBearer())])
async def logout(client_token: Annotated[str | None, Cookie()] = None):
    """Log Active User Out of System."""
    if client_token:
        close_session(client_token=client_token)
