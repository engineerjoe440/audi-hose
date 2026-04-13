################################################################################
"""
Audi-Hose
FOSS Speakpipe alternative built to connect audiences to the creators they love.

License: AGPL-3.0
Author: Joe Stanley
"""
################################################################################

import os
from pathlib import Path
from collections.abc import Mapping

from simple_toml_configurator import Configuration
from simple_toml_configurator.toml_configurator import ConfigObject


CONFIG_FILE_PATH = Path(os.getenv("CONFIG_FILE", "./config"))

DEFAULT_CONFIGURATION = {
    "application": {
        "site_url": "",
        "cross_site_origins": [],
        "storage_path": "",
    },
    "notifications": [],
}

# pylint: disable=no-member
class ConfigurationSettings(Configuration):
    """Base Configuration Data for Application."""

    def _set_os_env(self) -> None:
        """Override to safely skip non-table top-level config entries (e.g. [[notifications]])."""
        for table in self.config.copy():
            if not isinstance(self.config[table], Mapping):
                continue
            for key, value in self.config[table].items():
                existing_env = os.environ.get(self._make_env_name(table, key))
                if existing_env:
                    self.config[table][key] = self._parse_env_value(existing_env)
                    continue
                self._update_os_env(table, key, value)
        self._write_config_to_file()

    def _set_attributes(self) -> None:
        """Override to safely skip non-table top-level config entries (e.g. [[notifications]])."""
        for table in self.config:
            if not isinstance(self.config[table], Mapping):
                continue
            setattr(self, table, ConfigObject(self.config[table]))
            for key, value in self.config[table].items():
                setattr(self, f"_{table}_{key}", value)
                setattr(self, f"{table}_{key}", value)
                self._update_os_env(table, key, value)

    @property
    def notifications(self) -> list:
        """Return the list of configured notification channels from [[notifications]]."""
        return list(self.config.get("notifications", []) or [])

    @property
    def recordings_file_path(self) -> Path:
        """Evaluate the Correct Path, and Confirm that it Exists."""
        if not self.application.storage_path:
            self.application.storage_path = "./recordings"
        storage = Path(self.application.storage_path)
        storage.mkdir(parents=True, exist_ok=True)
        return storage


settings = ConfigurationSettings()
settings.init_config(
    config_path=CONFIG_FILE_PATH,
    defaults=DEFAULT_CONFIGURATION,
    config_file_name="app"
)
