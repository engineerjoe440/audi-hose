################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from fastapi import APIRouter

from . import recordings, accounts, groups

router = APIRouter(prefix="/api/v1")

router.include_router(accounts.router)
router.include_router(groups.router)
router.include_router(recordings.router)
