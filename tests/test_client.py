"""Tests for ONT client."""

import hashlib
from pathlib import Path

import pytest
import responses

from ont_stats.client import AuthenticationError, ONTClient


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def install_login_html():
    """Load install_login.html fixture."""
    return (FIXTURES_DIR / "install_login.html").read_text()


@pytest.fixture
def install_info_html():
    """Load install_info.html fixture."""
    return (FIXTURES_DIR / "install_info.html").read_text()


@pytest.fixture
def install_identifier_html():
    """Load install_identifier.html fixture."""
    return (FIXTURES_DIR / "install_identifier.html").read_text()


class TestONTClient:
    """Tests for ONTClient class."""

    def test_default_host(self):
        """Test default host configuration."""
        client = ONTClient()
        assert client.host == "192.168.100.1"
        assert client.base_url == "http://192.168.100.1"

    def test_custom_host(self):
        """Test custom host configuration."""
        client = ONTClient(host="192.168.1.1")
        assert client.host == "192.168.1.1"
        assert client.base_url == "http://192.168.1.1"

    def test_password_hash_computation(self):
        """Test MD5 hash computation for authentication."""
        client = ONTClient()
        password = "testpass"
        sid = "abc12345"

        result = client._compute_password_hash(password, sid)

        # Verify it's a valid MD5 hash
        expected = hashlib.md5(f"{password}:{sid}".encode()).hexdigest()
        assert result == expected

    def test_context_manager(self):
        """Test context manager protocol."""
        with ONTClient() as client:
            assert client.session is not None

    @responses.activate
    def test_get_session_id(self, install_login_html):
        """Test extracting session ID from login page."""
        responses.add(
            responses.GET,
            "http://192.168.100.1/cgi-bin/install_login.cgi",
            body=install_login_html,
            status=200,
        )

        client = ONTClient()
        sid = client._get_session_id()

        assert sid == "abc12345"

    @responses.activate
    def test_get_session_id_not_found(self):
        """Test error when session ID is not found."""
        responses.add(
            responses.GET,
            "http://192.168.100.1/cgi-bin/install_login.cgi",
            body="<html>No sid here</html>",
            status=200,
        )

        client = ONTClient()

        with pytest.raises(AuthenticationError, match="Could not extract session ID"):
            client._get_session_id()

    @responses.activate
    def test_login_success(self, install_login_html):
        """Test successful login."""
        # Mock login page GET
        responses.add(
            responses.GET,
            "http://192.168.100.1/cgi-bin/install_login.cgi",
            body=install_login_html,
            status=200,
        )

        # Mock login POST
        responses.add(
            responses.POST,
            "http://192.168.100.1/cgi-bin/install_login.cgi",
            body="<html>Welcome</html>",
            status=200,
        )

        client = ONTClient()
        client.login("admin", "password")

        assert client._logged_in is True

    @responses.activate
    def test_login_invalid_credentials(self, install_login_html):
        """Test login with invalid credentials."""
        responses.add(
            responses.GET,
            "http://192.168.100.1/cgi-bin/install_login.cgi",
            body=install_login_html,
            status=200,
        )

        responses.add(
            responses.POST,
            "http://192.168.100.1/cgi-bin/install_login.cgi",
            body="Falscher Benutzer oder Passwort",
            status=200,
        )

        client = ONTClient()

        with pytest.raises(AuthenticationError, match="Invalid username or password"):
            client.login("admin", "wrongpass")

    @responses.activate
    def test_fetch_install_info(self, install_login_html, install_info_html):
        """Test fetching install info page."""
        # Setup login
        responses.add(
            responses.GET,
            "http://192.168.100.1/cgi-bin/install_login.cgi",
            body=install_login_html,
            status=200,
        )
        responses.add(
            responses.POST,
            "http://192.168.100.1/cgi-bin/install_login.cgi",
            body="<html>Welcome</html>",
            status=200,
        )

        # Mock install_info page
        responses.add(
            responses.GET,
            "http://192.168.100.1/cgi-bin/install_info.cgi",
            body=install_info_html,
            status=200,
        )

        client = ONTClient()
        client.login("admin", "password")
        html = client.fetch_install_info()

        assert "gponPasswd" in html
        assert "MitraStar" in html

    def test_fetch_install_info_not_logged_in(self):
        """Test error when fetching without login."""
        client = ONTClient()

        with pytest.raises(RuntimeError, match="Not logged in"):
            client.fetch_install_info()

    @responses.activate
    def test_fetch_identifier(self, install_login_html, install_identifier_html):
        """Test fetching identifier page."""
        # Setup login
        responses.add(
            responses.GET,
            "http://192.168.100.1/cgi-bin/install_login.cgi",
            body=install_login_html,
            status=200,
        )
        responses.add(
            responses.POST,
            "http://192.168.100.1/cgi-bin/install_login.cgi",
            body="<html>Welcome</html>",
            status=200,
        )

        # Mock identifier page
        responses.add(
            responses.GET,
            "http://192.168.100.1/cgi-bin/install_identifier.cgi",
            body=install_identifier_html,
            status=200,
        )

        client = ONTClient()
        client.login("admin", "password")
        html = client.fetch_identifier()

        assert "gponStatus" in html
        assert "Connected" in html
