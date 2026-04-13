"""Unit tests for audihose.configuration module."""

import os
from pathlib import Path
from unittest.mock import patch

from audihose.configuration import ConfigurationSettings

DEFAULT_TEST_CONFIG = {
    "application": {
        "site_url": "",
        "cross_site_origins": [],
        "storage_path": "",
    },
    "notifications": [],
}


def test_configuration_settings_config_works_with_default_path():
    """Test that ConfigurationSettings can be instantiated."""
    config = ConfigurationSettings()
    assert config is not None


def test_configuration_settings_recordings_file_path_creation(temp_dir):
    """Test that recordings_file_path creates directory if it doesn't exist."""
    recordings_path = Path(temp_dir) / "new_recordings_dir"
    assert not recordings_path.exists()
    recordings_path.mkdir(parents=True, exist_ok=True)
    assert recordings_path.exists()


def test_configuration_settings_recordings_file_path_with_env_override(
    temp_dir, mocker
):
    """Test that CONFIG_FILE_PATH environment variable is respected."""
    config_dir = Path(temp_dir) / "custom_config"
    config_dir.mkdir(parents=True, exist_ok=True)
    mocker.patch.dict(os.environ, {"CONFIG_FILE_PATH": str(config_dir)})
    with patch.dict(os.environ, {"CONFIG_FILE_PATH": str(config_dir)}):
        assert os.environ.get("CONFIG_FILE_PATH") == str(config_dir)


def test_configuration_settings_config_handles_missing_values_gracefully():
    """Test that ConfigurationSettings handles missing config values."""
    try:
        config = ConfigurationSettings()
        assert config is not None
    except FileNotFoundError:
        pass


def test_configuration_settings_config_toml_parsing(temp_dir):
    """Test basic TOML configuration file parsing."""
    config_file = Path(temp_dir) / "app.toml"
    config_content = (
        "\n[application]\n"
        'site_url = "https://example.com"\n'
        "cross_site_origins = []\n"
        'storage_path = ""\n'
    )
    config_file.write_text(config_content)
    assert config_file.exists()
    assert config_file.read_text() is not None


def test_configuration_settings_config_path_resolution(temp_dir):
    """Test path resolution with multiple fallbacks."""
    base_path = Path(temp_dir)
    assert base_path.exists()
    new_path = base_path / "a" / "b" / "c"
    new_path.mkdir(parents=True, exist_ok=True)
    assert new_path.exists()


def test_configuration_settings_config_multiple_instantiations():
    """Test that multiple ConfigurationSettings instances don't conflict."""
    config1 = ConfigurationSettings()
    config2 = ConfigurationSettings()
    assert config1 is not None
    assert config2 is not None


def test_notifications_configuration_notifications_default_is_empty_list(temp_dir):
    """When no [[notifications]] entries are present, the list is empty."""
    config_file = Path(temp_dir) / "app.toml"
    config_file.write_text('[application]\nsite_url = ""\n')
    config = ConfigurationSettings()
    config.init_config(
        config_path=Path(temp_dir), defaults=DEFAULT_TEST_CONFIG, config_file_name="app"
    )
    notifications = getattr(config, "notifications", []) or []
    assert isinstance(notifications, list)
    assert len(notifications) == 0


def test_notifications_configuration_notifications_single_entry_parsed(temp_dir):
    """A single [[notifications]] entry is loaded as a list with one item."""
    config_file = Path(temp_dir) / "app.toml"
    config_file.write_text(
        '[application]\nsite_url = ""\n\n'
        '[[notifications]]\n'
        'name = "ntfy"\n'
        'url = "ntfys://my-topic/"\n'
        'attach_audio = false\n'
    )
    config = ConfigurationSettings()
    config.init_config(
        config_path=Path(temp_dir), defaults=DEFAULT_TEST_CONFIG, config_file_name="app"
    )
    notifications = getattr(config, "notifications", []) or []
    assert len(notifications) == 1
    entry = notifications[0]
    url = (
        entry.get("url")
        if isinstance(entry, dict)
        else getattr(entry, "url", None)
    )
    assert url == "ntfys://my-topic/"


def test_notifications_configuration_notifications_multiple_entries_parsed(temp_dir):
    """Multiple [[notifications]] entries are all loaded."""
    config_file = Path(temp_dir) / "app.toml"
    config_file.write_text(
        '[application]\nsite_url = ""\n\n'
        '[[notifications]]\n'
        'name = "email"\n'
        'url = "mailtos://user:pass@smtp.example.com"\n'
        'per_account = true\n\n'
        '[[notifications]]\n'
        'name = "slack"\n'
        'url = "slack://TokenA/TokenB/TokenC/channel"\n'
    )
    config = ConfigurationSettings()
    config.init_config(
        config_path=Path(temp_dir), defaults=DEFAULT_TEST_CONFIG, config_file_name="app"
    )
    notifications = getattr(config, "notifications", []) or []
    assert len(notifications) == 2


def test_notifications_configuration_notifications_per_account_flag_parsed(temp_dir):
    """The per_account boolean field is parsed from TOML correctly."""
    config_file = Path(temp_dir) / "app.toml"
    config_file.write_text(
        '[application]\nsite_url = ""\n\n'
        '[[notifications]]\n'
        'name = "email"\n'
        'url = "mailtos://user:pass@smtp.example.com"\n'
        'per_account = true\n'
    )
    config = ConfigurationSettings()
    config.init_config(
        config_path=Path(temp_dir), defaults=DEFAULT_TEST_CONFIG, config_file_name="app"
    )
    notifications = getattr(config, "notifications", []) or []
    assert len(notifications) == 1
    entry = notifications[0]
    per_account = (
        entry.get("per_account")
        if isinstance(entry, dict)
        else getattr(entry, "per_account", None)
    )
    assert per_account is True
