"""Tests for configuration loading."""

import tempfile
from pathlib import Path

import pytest

from ont_stats.config import ConfigError, load_credentials


def test_load_credentials_success():
    """Test loading valid credentials."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write("[ont]\n")
        f.write("username = testuser\n")
        f.write("password = testpass\n")
        f.flush()

        username, password = load_credentials(f.name)

        assert username == "testuser"
        assert password == "testpass"


def test_load_credentials_missing_file():
    """Test error when credentials file doesn't exist."""
    with pytest.raises(ConfigError, match="not found"):
        load_credentials("/nonexistent/path/credentials.ini")


def test_load_credentials_missing_section():
    """Test error when [ont] section is missing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write("[other]\n")
        f.write("key = value\n")
        f.flush()

        with pytest.raises(ConfigError, match="Missing \\[ont\\] section"):
            load_credentials(f.name)


def test_load_credentials_missing_username():
    """Test error when username is missing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write("[ont]\n")
        f.write("password = testpass\n")
        f.flush()

        with pytest.raises(ConfigError, match="Missing 'username'"):
            load_credentials(f.name)


def test_load_credentials_missing_password():
    """Test error when password is missing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write("[ont]\n")
        f.write("username = testuser\n")
        f.flush()

        with pytest.raises(ConfigError, match="Missing 'password'"):
            load_credentials(f.name)


def test_load_credentials_path_object():
    """Test that Path objects work as input."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write("[ont]\n")
        f.write("username = testuser\n")
        f.write("password = testpass\n")
        f.flush()

        username, password = load_credentials(Path(f.name))

        assert username == "testuser"
        assert password == "testpass"
