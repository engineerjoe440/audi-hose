################################################################################
"""
GrantSplat  -  Idaho 4-H Volunteer Association Grant Notifier
-------------------------------------------------------------

(c) 2023 - Stanley Solutions - License: MIT

Authors:
    - Joe Stanley
"""
################################################################################

from typing import Any, Union
import os
import logging
from pathlib import Path

import requests
from toml_config.core import Config

CONFIG_FILE_PATH = Path(os.getenv("CONFIG_FILE", "./config/app.conf"))

BOOL_LOOKUP = {
    "true": True,
    "false": False,
}


# Inject helper method to simplify modifying values on the fly.
def update(self: Config, key_name: str, value: str):
    """Update the Specified Key Name - Section Independent."""
    for section, data in self.config.items():
        if key_name in list(data.keys()):
            self.get_section(section)
            self.set(**{key_name: value})
Config.update = update


class ConfigurationData(object):
    """Base Configuration Data for Application."""
    # Generic Configuration Values
    site_url: str
    # Email Settings
    smtp_server: str
    smtp_port: int
    smtp_starttls: bool
    smtp_username: str
    smtp_password: str
    smtp_from_address: str
    # ntfy.sh Notification Settings
    ntfy_server_url: Union[str, None]
    ntfy_publication_topic: str
    ntfy_auth_token: Union[str, None]



class ConfigReader(ConfigurationData):
    """Read-Only Configuration Object."""
    _config: Config
    _logger: logging.Logger

    def __init__(self):
        """Initialize the Configuration."""
        CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._config = Config(str(CONFIG_FILE_PATH))
        self._logger = None
        # Generic Information
        self._config.add_section('Generic').set(
            site_url=os.getenv("SITE_URL", ""),
        )
        # Email Configuration
        self._config.add_section('Email').set(
            smtp_server=os.getenv("SMTP_SERVER", ""),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_starttls=BOOL_LOOKUP.get(
                os.getenv("SMTP_STARTTLS", "True").lower(),
                False
            ),
            smtp_username=os.getenv("SMTP_USERNAME", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            smtp_from_address=os.getenv(
                "SMTP_FROM_ADDRESS",
                "audihose@example.com"
            ),
        )
        # ntfy.sh Configuration
        self._config.add_section('ntfy.sh').set(
            ntfy_server_url=os.getenv("NTFY_SERVER", ""),
            ntfy_publication_topic=os.getenv("NTFY_TOPIC", "audihose"),
            ntfy_auth_token=os.getenv("NTFY_AUTH_TOKEN", ""),
        )

    def set_attributes(self):
        """Load Class Attributes."""
        for _, data in self._config.config.items():
            for key, value in data.items():
                self.__dict__[key] = value

    def ntfy(
        self,
        message: str,
        title: str = "GrantSplat Notification",
        priority: str | None = None,
        tags: list[str] | None = None,
    ):
        """Send ntfy.sh Notification."""
        if self.ntfy_server_url:
            # Set and Configure Headers Based on Loaded Data
            ntfy_headers = {"Title": title,}
            if priority:
                ntfy_headers["Priority"] = priority
            if tags:
                ntfy_headers["Tags"] = ",".join(tags)
            if self.ntfy_auth_token:
                # Set Authentication Token as Needed
                ntfy_headers["Authorization"] = f"Bearer {self.ntfy_auth_token}"
            requests.post(
                f"{self.ntfy_server_url}/{self.ntfy_publication_topic}",
                data=message,
                headers=ntfy_headers,
                timeout=60,
            )



class ConfigManager(ConfigReader):
    """Read/Write Configuration Management Interface."""

    def __init__(self):
        """Initialize the Configuration with Support for Updating Data."""
        super().__init__()
        # Load the Configuration into Class Attributes
        self.set_attributes()

    @property
    def config(self):
        """Return the Full Configuration."""
        return self._config.config

    def __setattr__(self, name: str, value: Any) -> None:
        """Magic Attribute Setter: Update the Config Object at the Same Time."""
        self.__dict__[name] = value
        self._config.update(name, value)
        self._config.save()