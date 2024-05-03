################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################
# pylint: disable=no-member

import os
from pathlib import Path


CONFIG_FILE_PATH = Path(os.getenv("CONFIG_FILE", "./config/app.conf"))

DEFAULT_CONFIGURATION = {
    "application": {
        "site_url": "",
        "cross_site_origins": [],
        "storage_path": "",
    },
    "smtp": {
        "server": "",
        "port": 587,
        "starttls": True,
        "username": "",
        "password": "",
        "from_address": "audihose@example.com",
    },
    "ntfy": {
        "server": "",
        "topic": "audihose",
        "token": "",
    }
}

class ConfigurationSettings:
    """Base Configuration Data for Application."""

    @property
    def recordings_file_path(self) -> Path:
        """Evaluate the Correct Path, and Confirm that it Exists."""


settings = ConfigurationSettings()
