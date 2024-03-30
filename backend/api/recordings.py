################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

try:
    from backend.database.models import Recording
except ImportError:
    from database.models import Recording


router = APIRouter(prefix="/recordings")

@router.get("/")
async def get_all_recordings() -> list[Recording]:
    """Get the List of all Recordings."""
    return await Recording.all()

@router.get("/{recording_id}")
async def get_single_recording(recording_id: str) -> StreamingResponse:
    """Get a Single Recording's Audio File."""
    recording = await Recording.get(id=recording_id)

    def inner_iter():
        with open(recording.path, 'rb') as audio_file:
            yield from audio_file

    return StreamingResponse(inner_iter(), media_type="audio/mp3")

@router.get("/by-path/")
async def get_recording_by_path(recording_path: str) -> StreamingResponse:
    """Get a Single Recording's Audio File."""
    def inner_iter():
        with open(recording_path, 'rb') as audio_file:
            yield from audio_file

    return StreamingResponse(inner_iter(), media_type="audio/mp3")

@router.put("/")
async def create_new_recording(new_recording: Recording) -> int:
    """Create a New Recording."""
    return await new_recording.insert()
