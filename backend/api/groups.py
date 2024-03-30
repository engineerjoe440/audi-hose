################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from typing import Annotated

from fastapi import APIRouter, Depends, Cookie
from fastapi.responses import Response, RedirectResponse


router = APIRouter(prefix="/groups")