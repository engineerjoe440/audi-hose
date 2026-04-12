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
    Request, APIRouter, HTTPException, status, Query, Cookie, Depends, Response, Header
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from loguru import logger
from sqlmodel import select

from .sessions import (
    get_session,
    close_session,
    SessionManager,
    REMEMBER_ME_INACTIVITY_SECONDS,
)
from .database import Account, Login, NewAccountData, SessionDependency
from .security import verify_token, decode_jwt, check_password, sign_jwt
from .api.accounts import create_account


router = APIRouter()
REVOKED_TOKENS: set[str] = set()


class LoginItem(BaseModel):
    """Login Parameters."""
    email: str
    password: str
    client_token: str | None = None
    remember_me: bool = False

class TokenResponse(BaseModel):
    """JSON Web Token Response for Authentication."""
    token: Union[str, None] = None
    message: Union[str, None] = None


COOKIE_NAME = "client_token"


def _set_client_cookie(
    response: Response,
    client_token: str,
    remember_me: bool,
):
    """Set client token persistence based on remember-me mode."""
    if remember_me:
        response.set_cookie(
            COOKIE_NAME,
            client_token,
            max_age=REMEMBER_ME_INACTIVITY_SECONDS,
        )
    else:
        response.set_cookie(COOKIE_NAME, client_token)


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
            # Check that Session is Still Active
            token_payload = decode_jwt(credentials.credentials)
            session_token = token_payload.get("session") if token_payload else None
            if not session_token or not get_session(session_token):
                logger.warning("Session Expired.")
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
def user_login(
    login_item: LoginItem,
    response: Response,
    session: SessionDependency,
) -> TokenResponse:
    """Authenticate admin user and provide a JSON Web Token."""
    client_token = login_item.client_token or SessionManager.create_session()
    user_session = get_session(client_token=client_token)
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="could not identify active session object, please reload",
        )

    data = jsonable_encoder(login_item)
    email = data["email"]
    password = data["password"]

    login_response = TokenResponse(message="Invalid Credentials.")
    remember_me = bool(data.get("remember_me", False))

    try:
        # Obtain the Account Corresponding to the User Email
        account = session.exec(
            select(Account).where(Account.email == email)
        ).first()
        if account and account.id is not None:
            login_db_entry = session.exec(
                select(Login).where(Login.account_id == account.id)
            ).first()
            if login_db_entry and check_password(
                password,
                login_db_entry.hashed_password,
            ):
                user_session.configure_authenticated(remember_me=remember_me)
                login_response.token = sign_jwt({
                    "email": email,
                    "id": account.id,
                    "session": user_session.client_token,
                }, expiry_seconds=user_session.jwt_expiry_seconds)
                login_response.message = None
                user_session.email = email
                user_session.account_id = account.id
                _set_client_cookie(
                    response,
                    client_token=user_session.client_token,
                    remember_me=remember_me,
                )
    except ValueError as err:
        login_response.message = (
            f"Server failure: '{err}'\n"
            "If this issue persists, contact administrator."
        )
        logger.exception(err)
    return login_response

@router.post(
    "/refresh-token",
    dependencies=[Depends(JWTBearer())],
    response_model=TokenResponse
)
def refresh_token(
    response: Response,
    client_token: Annotated[str | None, Cookie()] = None
) -> TokenResponse:
    """Refresh the JSON Web Token for an Authenticated admin User."""
    token = TokenResponse()
    if client_token:
        session = get_session(client_token=client_token)
        if session:
            _set_client_cookie(
                response,
                client_token=session.client_token,
                remember_me=session.remember_me,
            )
            token.token = sign_jwt({
                "email": session.email,
                "id": session.account_id,
                "session": session.client_token,
            }, expiry_seconds=session.jwt_expiry_seconds)
    return token

@router.post("/logout", dependencies=[Depends(JWTBearer())])
def logout(client_token: Annotated[str | None, Cookie()] = None):
    """Log Active User Out of System."""
    if client_token:
        close_session(client_token=client_token)

@router.get("/signup-required")
def determine_signup_status(session: SessionDependency) -> bool:
    """Determine Whether a User Must be Created, First."""
    return session.exec(select(Account.id)).first() is None

@router.post("/create-initial-account")
def create_initial_account(
    initial_account_data: NewAccountData,
    session: SessionDependency,
    client_token: Annotated[str | None, Cookie()] = None,
) -> TokenResponse:
    """Create the Very First Account."""
    if session.exec(select(Account.id)).first() is None:
        account_id = create_account(
            session=session,
            account_data=initial_account_data,
        )
        token = TokenResponse()
        user_session = get_session(client_token=client_token)
        token.token = sign_jwt({
            "email": initial_account_data.email,
            "id": account_id,
            "session": client_token,
        })
        if user_session is not None:
            user_session.email = initial_account_data.email
            user_session.account_id = account_id
        return token
    raise HTTPException(
        status_code=status.HTTP_423_LOCKED,
        detail="Cannot create a new account."
    )


def require_bearer_token_only(authorization: str | None = Header(default=None)):
    """Compatibility auth check that validates JWT signature only."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    token = authorization.split(" ", 1)[1].strip()
    if not token or not verify_token(token=token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if token in REVOKED_TOKENS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return token


@router.post("/api/v1/auth/login")
def user_login_compat(
    login_item: LoginItem,
    response: Response,
    session: SessionDependency,
):
    """Compatibility login endpoint."""
    result = user_login(login_item=login_item, response=response, session=session)
    if result.token:
        return {"access_token": result.token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=result.message)


@router.post("/api/v1/auth/refresh", dependencies=[Depends(require_bearer_token_only)])
@router.post("/api/v1/auth/refresh-token", dependencies=[Depends(require_bearer_token_only)])
def refresh_token_compat(
    response: Response,
    client_token: Annotated[str | None, Cookie()] = None,
):
    """Compatibility refresh endpoint."""
    result = refresh_token(response=response, client_token=client_token)
    return {"access_token": result.token, "token_type": "bearer"}


@router.post("/api/v1/auth/logout", dependencies=[Depends(require_bearer_token_only)])
def logout_compat(
    client_token: Annotated[str | None, Cookie()] = None,
    authorization: str | None = Header(default=None),
):
    """Compatibility logout endpoint."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
        if token:
            REVOKED_TOKENS.add(token)
    logout(client_token=client_token)
    return {"status": "ok"}


@router.get("/api/v1/auth/signup-status")
def determine_signup_status_compat(session: SessionDependency):
    """Compatibility signup status endpoint."""
    return {"signup_enabled": determine_signup_status(session=session)}


@router.post("/api/v1/auth/sign-up")
def create_initial_account_compat(
    initial_account_data: NewAccountData,
    session: SessionDependency,
    client_token: Annotated[str | None, Cookie()] = None,
):
    """Compatibility initial-account endpoint."""
    result = create_initial_account(
        initial_account_data=initial_account_data,
        session=session,
        client_token=client_token,
    )
    return {"access_token": result.token, "token_type": "bearer"}
