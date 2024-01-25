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
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application Lifespan System."""
    # Setup
    yield
    # Teardown
