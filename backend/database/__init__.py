################################################################################
"""
Audi-Hose
Connecting audiences to the creators they love with easy audio.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

from pathlib import Path

from pydbantic import Database

try:
    from backend.database.models import (
        Account, Login, Recording, PublicationGroup
    )
except ImportError:
    from database.models import (
        Account, Login, Recording, PublicationGroup
    )


async def connect_database(
    database_path: str = "db/datastore",
    testing: bool = False,
) -> Database:
    """Connect to the Database and Manage any Automatic Migrations Needed."""
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)
    return await Database.create(
        f'sqlite:///{database_path}.db',
        tables=[Account, Login, Recording, PublicationGroup],
        testing=testing,
    )
