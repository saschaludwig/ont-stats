"""Configuration loading for ONT Stats."""

import configparser
from pathlib import Path


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""

    pass


def load_credentials(path: Path | str = "credentials.ini") -> tuple[str, str]:
    """
    Load ONT credentials from an INI file.

    Args:
        path: Path to the credentials INI file. Defaults to 'credentials.ini'.

    Returns:
        Tuple of (username, password).

    Raises:
        ConfigError: If the file is missing, or required keys are not present.
    """
    path = Path(path)

    if not path.exists():
        raise ConfigError(f"Credentials file not found: {path}")

    config = configparser.ConfigParser()
    config.read(path)

    if "ont" not in config:
        raise ConfigError(f"Missing [ont] section in {path}")

    section = config["ont"]

    if "username" not in section:
        raise ConfigError(f"Missing 'username' in [ont] section of {path}")

    if "password" not in section:
        raise ConfigError(f"Missing 'password' in [ont] section of {path}")

    return section["username"], section["password"]
