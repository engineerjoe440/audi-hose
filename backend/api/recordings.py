################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from typing import Annotated, Optional
from uuid import uuid4

from fastapi import APIRouter, File
from fastapi.responses import StreamingResponse
from pydantic import EmailStr

try:
    from backend.database.models import Recording, PublicationGroup
    from backend.configuration import ConfigReader
except ImportError:
    from database.models import Recording, PublicationGroup
    from configuration import ConfigReader


router = APIRouter(prefix="/recordings")

@router.get("/")
async def get_all_recordings() -> list[Recording]:
    """Get the List of all Recordings."""
    return await Recording.all()

@router.get("/group/{group_id}")
async def get_recordings_by_group(group_id: str) -> list[Recording]:
    """Get the Recordings by Group ID."""
    group = await PublicationGroup.get(id=group_id)
    return await Recording.filter(group=group)

@router.get("/{recording_id}")
async def get_single_recording(recording_id: str) -> StreamingResponse:
    """Get a Single Recording's Audio File."""
    recording = await Recording.get(id=recording_id)

    def inner_iter():
        with open(recording.path, 'rb') as audio_file:
            yield from audio_file

    return StreamingResponse(inner_iter(), media_type="audio/mp3")

@router.put("/")
async def create_new_recording(
    subject: str,
    group_id: str,
    recording: Annotated[bytes, File()],
    email: Optional[EmailStr] = None,
) -> str:
    """Create a New Recording."""
    recording_id = str(uuid4())
    # Store the File Contents
    config = ConfigReader().set_attributes()
    file_path = config.recordings_file_path / f"{recording_id}.wav"
    with open(file_path, 'wb') as dst_file_obj:
        dst_file_obj.write(recording)
    # Look Up the Group
    group = await PublicationGroup.get(id=group_id)
    # Record the New Audio Recording in the Database
    await Recording.create(
        id=recording_id,
        subject=subject,
        email=email,
        group=group,
    )
    return recording_id

@router.post("/notify/{recording_id}")
async def send_new_data_notification(recording_id: str):
    """Send the Notification of a New Recording."""
    recording = await Recording.get(id=recording_id)
    for _ in recording.group.accounts:
        # Publish Notification for Account
        ...
