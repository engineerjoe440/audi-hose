################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from typing import Union
from uuid import uuid4
from datetime import datetime
from enum import Enum

from pydantic import EmailStr
from pydbantic import DataBaseModel

class Account(DataBaseModel):
    """Single Account."""
    id: str = PrimaryKey(default=lambda: str(uuid4()))
    name: str
    email: EmailStr
    hashed_password: str

class Recording(DataBaseModel):
    """Single Recording Reference."""
    id: str = PrimaryKey(default=lambda: str(uuid4()))
    path: str
    subject_name: str
    email: EmailStr
