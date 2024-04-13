################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from typing import Annotated

from fastapi import APIRouter, Depends, Cookie
from fastapi.responses import Response, RedirectResponse

try:
    from backend.api import recordings, accounts, groups
except ImportError:
    from api import recordings, accounts, groups

router = APIRouter(prefix="/api/v1")

router.include_router(accounts.router)
router.include_router(groups.router)
router.include_router(recordings.router)
