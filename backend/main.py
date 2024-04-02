################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

import datetime
from typing import Annotated
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger

try:
    from backend import __header__, __version__, api, authentication
    from backend.database import connect_database
    from backend.database.models import Account
    from backend.sessions import SessionManager, get_session
except ImportError:
    import api
    import authentication
    from __init__ import __header__, __version__
    from database import connect_database
    from database.models import Account
    from sessions import SessionManager, get_session


__html_header__ = __header__.replace("\n", r"\n")

APP_COOKIE_NAME = "client_token"

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application Lifespan System."""
    # Setup
    logger.debug(__header__)
    # Connect Database
    _ = await connect_database()
    yield
    # Teardown

app = FastAPI(
    title="AudiHose",
    summary=(
        "FOSS Speakpipe alternative built to connect audiences to the creators "
        "they love."
    ),
    version=__version__,
    lifespan=lifespan,
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
async def root(
    request: Request,
    client_token: Annotated[str | None, Cookie()] = None,
) -> HTMLResponse:
    """Server Root."""
    template = "index.html"
    if not client_token:
        client_token = SessionManager.create_session()
        template="landing.html"
    elif not get_session(client_token=client_token):
        client_token = SessionManager.create_session()
        template="landing.html"
    elif get_session(client_token=client_token).email is None:
        template="landing.html"
    account_id = get_session(client_token=client_token).account_id
    context = {
        "request": request,
        APP_COOKIE_NAME: client_token,
        "console_app_name": __html_header__,
        "year": datetime.datetime.now().year
    }
    if account_id is not None:
        context["account_name"] = (await Account.get(id=account_id)).name
    # Fall Back to Landing Page
    response = TEMPLATES.TemplateResponse(
        template,
        context,
    )
    response.set_cookie(APP_COOKIE_NAME, client_token)
    return response

@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
@app.get("/component", response_class=HTMLResponse, include_in_schema=False)
async def app_base(
    request: Request,
    client_token: Annotated[str | None, Cookie()] = None,
) -> HTMLResponse:
    """Application Base."""
    if not client_token:
        client_token = SessionManager.create_session()
    elif not get_session(client_token=client_token):
        client_token = SessionManager.create_session()
    # Fall Back to Landing Page
    response = TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            APP_COOKIE_NAME: client_token,
            "console_app_name": __html_header__,
        },
    )
    response.set_cookie(APP_COOKIE_NAME, client_token)
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
    # api.config.ntfy(
    #     message=(
    #         f"Failed HTTP Method: {request.method} at URL: {request.url}.\n"
    #         f"{email_desc}Exception Message: {exc!r}"
    #     ),
    #     title="ScrapbookZ Failure",
    #     priority="urgent",
    #     tags=["warning", "skull"]
    # )
    # if email_desc:
    #     api.config.logger.error("User Encountered Error -- %s", email_desc)
    # api.config.logger.exception(exc)
    raise exc
