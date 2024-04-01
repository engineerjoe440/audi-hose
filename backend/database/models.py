################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from uuid import uuid4
from datetime import datetime

from pydantic import EmailStr
from pydbantic import DataBaseModel, PrimaryKey

class Account(DataBaseModel):
    """Single Account."""
    id: str = PrimaryKey(default=lambda: str(uuid4()))
    name: str
    email: EmailStr
    hashed_password: str

class PublicationGroup(DataBaseModel):
    """Grouping of Accounts to Receive Notification of a New Recording."""
    id: str = PrimaryKey(default=lambda: str(uuid4()))
    name: str
    accounts: list[Account]
    description: str = ""

class Recording(DataBaseModel):
    """Single Recording Reference."""
    id: str = PrimaryKey(default=lambda: str(uuid4()))
    time: datetime = datetime.now()
    subject: str
    email: EmailStr
    group: PublicationGroup
