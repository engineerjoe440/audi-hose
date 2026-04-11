################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################
# pylint: disable=no-member

import datetime
from typing import Annotated
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from . import __header__, __version__, api, authentication
from .configuration import settings
from .database import (
    Account,
    SessionDependency,
    create_database_tables,
    DEFAULT_GROUP_ID,
)
from .sessions import (
    SessionManager,
    get_session,
    REMEMBER_ME_INACTIVITY_SECONDS,
)
from .notifier import ntfy_publish


__html_header__ = __header__.replace("\n", r"\n")

APP_COOKIE_NAME = "client_token"


def _set_session_cookie(response: HTMLResponse, client_token: str):
    """Apply cookie persistence policy based on session remember-me state."""
    active_session = get_session(client_token=client_token)
    if active_session and active_session.remember_me:
        response.set_cookie(
            APP_COOKIE_NAME,
            client_token,
            max_age=REMEMBER_ME_INACTIVITY_SECONDS,
        )
    else:
        response.set_cookie(APP_COOKIE_NAME, client_token)

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application Lifespan System."""
    # Setup
    logger.info(__header__)
    # Connect Database
    create_database_tables()
    # Create Default Submission Group
    # pylint: disable=global-statement
    yield
    # Teardown

app = FastAPI(
    title="AudiHose",
    summary="Connecting audiences to the creators they love with easy audio.",
    version=__version__,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000", # Uvicorn Default Server
    ] + settings.application.cross_site_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api.router)
app.include_router(authentication.router)

# Mount the Static File Path
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent/"static"),
    name="static"
)

# Load Templates
TEMPLATES: Jinja2Templates = Jinja2Templates(
    directory=(Path(__file__).parent/"templates"),
)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root(
    request: Request,
    session: SessionDependency,
    client_token: Annotated[str | None, Cookie()] = None,
) -> HTMLResponse:
    """Server Root."""
    template = "index.html"
    active_session = get_session(client_token=client_token) if client_token else None
    if not client_token:
        client_token = SessionManager.create_session()
        active_session = get_session(client_token=client_token)
        template = "landing.html"
    elif not active_session:
        client_token = SessionManager.create_session()
        active_session = get_session(client_token=client_token)
        template = "landing.html"
    elif active_session.email is None:
        template = "landing.html"
    account_id = active_session.account_id if active_session else None
    context = {
        "request": request,
        APP_COOKIE_NAME: client_token,
        "console_app_name": __html_header__,
        "year": datetime.datetime.now().year,
    }
    if account_id is not None:
        account = session.get(Account, account_id)
        if account is not None:
            context["account_name"] = account.name
    # Fall Back to Landing Page
    response = TEMPLATES.TemplateResponse(
        request,
        template,
        context=context,
    )
    _set_session_cookie(response, client_token)
    return response


@app.get("/component", response_class=HTMLResponse, include_in_schema=False)
def component_root(
    request: Request,
    client_token: Annotated[str | None, Cookie()] = None,
) -> HTMLResponse:
    """Server Root."""
    active_session = get_session(client_token=client_token) if client_token else None
    if not client_token:
        client_token = SessionManager.create_session()
    elif not active_session:
        client_token = SessionManager.create_session()
    # Fall Back to Landing Page
    response = TEMPLATES.TemplateResponse(
        request,
        "component.html",
        context={
            "request": request,
            APP_COOKIE_NAME: client_token,
            "console_app_name": __html_header__,
            "year": datetime.datetime.now().year,
            "host_url": settings.application.site_url,
            "default_group_id": DEFAULT_GROUP_ID,
        },
    )
    _set_session_cookie(response, client_token)
    return response

@app.get("/component.js", response_class=RedirectResponse, include_in_schema=False)
def component_redirect() -> RedirectResponse:
    """Redirect for the Standard Embed-Able Component."""
    return RedirectResponse(url="/static/react/js/main.js")

@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
@app.get("/sign-up", response_class=HTMLResponse, include_in_schema=False)
def app_base(
    request: Request,
    client_token: Annotated[str | None, Cookie()] = None,
) -> HTMLResponse:
    """Application Base."""
    active_session = get_session(client_token=client_token) if client_token else None
    if not client_token:
        client_token = SessionManager.create_session()
    elif not active_session:
        client_token = SessionManager.create_session()
    # Fall Back to Landing Page
    response = TEMPLATES.TemplateResponse(
        request,
        "index.html",
        context={
            "request": request,
            APP_COOKIE_NAME: client_token,
            "console_app_name": __html_header__,
        },
    )
    _set_session_cookie(response, client_token)
    return response

################################################################################

@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    """Global Exception-Handling Middleware - Reports Errors where Needed."""
    # Attempt Identification of the Client User
    try:
        client_token = request.cookies.get(APP_COOKIE_NAME)
        session = get_session(client_token=client_token)
        email_desc = f"User Email: {session.email}\n"
    except (AttributeError, KeyError):
        email_desc = ""
    # Alert Subscribers to the Exception
    ntfy_publish(
        message=(
            f"Failed HTTP Method: {request.method} at URL: {request.url}.\n"
            f"{email_desc}Exception Message: {exc!r}"
        ),
        title="AudiHose Failure",
        priority="urgent",
        tags=["warning", "skull"]
    )
    if email_desc:
        logger.error("User Encountered Error -- %s", email_desc)
    logger.exception(exc)
    raise exc
