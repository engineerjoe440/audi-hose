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

from fastapi import APIRouter, Depends, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import EmailStr
from sqlalchemy.orm import selectinload
from sqlmodel import select

from ..database import (
    PublicationGroup,
    Recording,
    RecordingRead,
    SessionDependency,
    to_recording_read,
)
from ..configuration import settings
from ..notifier import send_email_message
from .common import get_group_or_404, require_api_auth


router = APIRouter(prefix="/recordings")

@router.get("/", dependencies=[Depends(require_api_auth)])
def get_all_recordings(session: SessionDependency) -> list[RecordingRead]:
    """Get the List of all Recordings."""
    recordings = session.exec(
        # pylint: disable-next=E1101
        select(Recording).order_by(Recording.time.desc()) #noqa: E1101
    ).all()
    return [to_recording_read(recording) for recording in recordings]

@router.get("/group/{group_id}", dependencies=[Depends(require_api_auth)])
def get_recordings_by_group(
    group_id: str,
    session: SessionDependency,
) -> list[RecordingRead]:
    """Get the Recordings by Group ID."""
    group = get_group_or_404(session=session, group_id=group_id)
    if not group.accepting_submissions:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Group is not accepting submissions.",
        )
    recordings = session.exec(
        select(Recording)
        .where(Recording.group_id == group_id)
        # pylint: disable-next=E1101
        .order_by(Recording.time.desc()) #noqa: E1101
    ).all()
    return [to_recording_read(recording) for recording in recordings]

@router.get("/{recording_id}", dependencies=[Depends(require_api_auth)])
def get_single_recording(
    recording_id: str,
    session: SessionDependency,
) -> StreamingResponse:
    """Get a Single Recording's Audio File."""
    recording = session.get(Recording, recording_id)
    if recording is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found.",
        )

    def inner_iter():
        with open(recording.file_path, 'rb') as audio_file:
            yield from audio_file

    return StreamingResponse(inner_iter(), media_type="audio/mp3")

@router.put("/", dependencies=[Depends(require_api_auth)])
def create_new_recording(
    subject: str,
    group_id: str,
    session: SessionDependency,
    recording: Annotated[bytes, File()],
    email: Optional[EmailStr] = None,
) -> str:
    """Create a New Recording."""
    recording_id = str(uuid4())
    # Store the File Contents
    file_path = settings.recordings_file_path / f"{recording_id}.wav"
    with open(file_path, 'wb') as dst_file_obj:
        dst_file_obj.write(recording)
    # Look Up the Group
    group = get_group_or_404(session=session, group_id=group_id)
    if not group.accepting_submissions:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Group is not accepting submissions.",
        )
    # Record the New Audio Recording in the Database
    db_recording = Recording(
        id=recording_id,
        subject=subject,
        email=email,
        file_path=str(file_path),
        group_id=group.id,
    )
    session.add(db_recording)
    session.commit()
    return recording_id

@router.post("/notify/{recording_id}", dependencies=[Depends(require_api_auth)])
@router.post("/{recording_id}/notify", dependencies=[Depends(require_api_auth)])
def send_new_data_notification(
    recording_id: str,
    session: SessionDependency,
):
    """Send the Notification of a New Recording."""
    recording = session.exec(
        select(Recording)
        .where(Recording.id == recording_id)
        .options(
            selectinload(Recording.group)
            .selectinload(PublicationGroup.accounts)
        )
    ).first()
    if recording is None or recording.group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found.",
        )
    subject = "New Recording!"
    if recording.subject:
        subject += f" '{recording.subject}'"
    for account in recording.group.accounts:
        # Publish Notification for Account
        send_email_message(
            subject=subject,
            template="",
            to_address=account.email,
            #kwargs
        )
    return {"status": "ok"}


@router.post("/", dependencies=[Depends(require_api_auth)])
def create_new_recording_post(
    session: SessionDependency,
    file: Annotated[bytes, File()],
    subject: str = Form(...),
    group_id: str = Form(...),
    email: Optional[EmailStr] = Form(default=None),
) -> RecordingRead:
    """Compatibility endpoint for POST + file upload with `file` field name."""
    recording_id = create_new_recording(
        subject=subject,
        group_id=group_id,
        session=session,
        recording=file,
        email=email,
    )
    created = session.get(Recording, recording_id)
    if created is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Recording creation failed.",
        )
    return to_recording_read(created)
