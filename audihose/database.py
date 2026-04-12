################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from pathlib import Path
from typing import Annotated, List, Optional
from uuid import uuid4
from datetime import datetime

from fastapi import Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, DateTime
from sqlmodel import (
    Field, Relationship, SQLModel, Session, create_engine, select
)

from .configuration import CONFIG_FILE_PATH

storage_path = CONFIG_FILE_PATH
storage_directory = Path(storage_path)
storage_directory.mkdir(parents=True, exist_ok=True)

DB_FILE = storage_directory / "audihose.db"
BACKUP_FILE = DB_FILE.with_suffix(".backup")

ECHO = False

DEFAULT_GROUP_NAME = "DEFAULT-PUBLICATION-GROUP"
DEFAULT_GROUP_ID = None


##  Models  ####################################################################


def generate_identifier() -> str:
    """Create a Stable UUID String Identifier."""
    return str(uuid4())


class NewAccountData(BaseModel):
    """Data Required for a New Account."""
    name: str
    email: EmailStr
    password: str


class AccountData(BaseModel):
    """Data Needed for an Account."""
    name: str
    email: EmailStr


class AccountSummary(AccountData):
    """API Response for a Single Account."""
    id: str


class PublicationGroupSummary(BaseModel):
    """API Response for a Publication Group."""
    id: str
    name: str
    accepting_submissions: bool = True


class PublicationGroupCreate(BaseModel):
    """Data Required to Create a New Group."""
    name: str
    accepting_submissions: bool = True


class PublicationGroupUpdate(PublicationGroupCreate):
    """Data Required to Modify an Existing Group."""
    id: str


class AccountMembershipUpdate(BaseModel):
    """Replacement Membership List for a Group."""
    account_ids: List[str]


class RecordingRead(BaseModel):
    """API Response for a Recording."""
    id: str
    time: datetime
    subject: str
    email: Optional[EmailStr] = None
    group_id: str
    file_path: str


class PublicationGroupAccountLink(SQLModel, table=True):
    """Link Table for Account Membership in Publication Groups."""
    __tablename__ = "publication_group_account_link"

    group_id: str = Field(
        foreign_key="publication_group.id",
        primary_key=True,
        alias="publication_group_id",
    )
    account_id: str = Field(foreign_key="account.id", primary_key=True)


class Account(SQLModel, table=True):
    """Single Account."""
    __tablename__ = "account"

    id: str = Field(default_factory=generate_identifier, primary_key=True)
    name: str
    email: EmailStr = Field(index=True, unique=True)
    login: Optional["Login"] = Relationship(back_populates="account")
    groups: List["PublicationGroup"] = Relationship(
        back_populates="accounts",
        link_model=PublicationGroupAccountLink,
    )


class Login(SQLModel, table=True):
    """Login Information for a Singular Account."""
    __tablename__ = "login"

    id: str = Field(default_factory=generate_identifier, primary_key=True)
    account_id: str = Field(foreign_key="account.id", index=True)
    hashed_password: str
    account: Optional["Account"] = Relationship(back_populates="login")


class PublicationGroup(SQLModel, table=True):
    """Grouping of Accounts to Receive Notification of a New Recording."""
    __tablename__ = "publication_group"

    id: str = Field(default_factory=generate_identifier, primary_key=True)
    name: str
    accepting_submissions: bool = True
    accounts: List["Account"] = Relationship(
        back_populates="groups",
        link_model=PublicationGroupAccountLink,
    )
    recordings: List["Recording"] = Relationship(back_populates="group")


class AccountWithGroups(AccountData):
    """Account With Groups Information."""
    id: str
    associations: List[PublicationGroupSummary]

    @property
    def groups(self) -> List[PublicationGroupSummary]:
        """Backward-compatible alias for associations."""
        return self.associations


class Recording(SQLModel, table=True):
    """Single Recording Reference."""
    __tablename__ = "recording"

    id: str = Field(default_factory=generate_identifier, primary_key=True)
    time: datetime = Field(sa_column=Column(DateTime, default=datetime.utcnow))
    subject: str
    email: Optional[EmailStr] = None
    file_path: str
    group_id: str = Field(foreign_key="publication_group.id", index=True)
    group: Optional[PublicationGroup] = Relationship(back_populates="recordings")


def to_account_summary(account: Account) -> AccountSummary:
    """Convert a Table Model to an API Account Payload."""
    return AccountSummary(id=account.id, name=account.name, email=account.email)


def to_group_summary(group: PublicationGroup) -> PublicationGroupSummary:
    """Convert a Table Model to an API Group Payload."""
    return PublicationGroupSummary(
        id=group.id,
        name=group.name,
        accepting_submissions=group.accepting_submissions,
    )


def to_account_with_groups(account: Account) -> AccountWithGroups:
    """Convert an Account and its Relationships to an API Payload."""
    return AccountWithGroups(
        id=account.id,
        name=account.name,
        email=account.email,
        associations=[to_group_summary(group) for group in account.groups],
    )


def to_recording_read(recording: Recording) -> RecordingRead:
    """Convert a Recording to an API Payload."""
    return RecordingRead(
        id=recording.id,
        time=recording.time,
        subject=recording.subject,
        email=recording.email,
        group_id=recording.group_id,
        file_path=recording.file_path,
    )

engine = create_engine(f"sqlite:///{DB_FILE}", echo=ECHO)
session: Optional[Session] = None

DB_FILE.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    f"sqlite:///{DB_FILE}",
    connect_args={"check_same_thread": False},
    echo=ECHO,
)
SQLModel.metadata.create_all(engine)

if session is not None:
    session.close()
session = Session(engine)


def get_session():
    """Provide per-request session instances for FastAPI dependencies."""
    with Session(engine) as db_session:
        yield db_session


SessionDependency = Annotated[Session, Depends(get_session)]


def ensure_default_publication_group(db_session: Optional[Session] = None) -> str:
    """Create the default group once and return its identifier.

    Accepts an optional explicit session for test compatibility.
    """
    active_session = db_session or session
    default_group = active_session.exec(
        select(PublicationGroup).where(PublicationGroup.name == DEFAULT_GROUP_NAME)
    ).first()
    if default_group is None:
        default_group = PublicationGroup(name=DEFAULT_GROUP_NAME)
        active_session.add(default_group)
        active_session.commit()
        active_session.refresh(default_group)
    return default_group.id


def create_database_tables():
    """Create Database Tables."""
    SQLModel.metadata.create_all(engine)
    ensure_default_publication_group()
