################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

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
    from backend.sessions import SessionManager, get_session
except ImportError:
    import api
    import authentication
    from __init__ import __header__, __version__
    from database import connect_database
    from sessions import SessionManager, get_session


__html_header__ = __header__.replace("\n", r"\n")

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
@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
@app.get("/component", response_class=HTMLResponse, include_in_schema=False)
async def root(
    request: Request,
    client_token: Annotated[str | None, Cookie()] = None,
) -> HTMLResponse:
    """Server Root."""
    if not client_token:
        client_token = SessionManager.create_session()
    elif not get_session(client_token=client_token):
        client_token = SessionManager.create_session()
    response = TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "client_token": client_token,
            "console_app_name": __html_header__,
        },
    )
    response.set_cookie("client_token", client_token)
    return response
