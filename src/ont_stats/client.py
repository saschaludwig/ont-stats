"""HTTP client for ONT device communication."""

import hashlib
import re

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class AuthenticationError(Exception):
    """Raised when authentication with the ONT fails."""

    pass


class ONTClient:
    """Client for communicating with MitraStar ONT devices."""

    DEFAULT_HOST = "192.168.100.1"
    DEFAULT_TIMEOUT = 10

    # Regex to extract session ID from login page JavaScript
    SID_PATTERN = re.compile(r"var\s+sid\s*=\s*['\"]([a-fA-F0-9]+)['\"]")

    def __init__(self, host: str | None = None, timeout: int | None = None):
        """
        Initialize the ONT client.

        Args:
            host: ONT IP address or hostname. Defaults to 192.168.100.1.
            timeout: Request timeout in seconds. Defaults to 10.
        """
        self.host = host or self.DEFAULT_HOST
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.base_url = f"http://{self.host}"

        # Set up session with retry logic
        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)

        self._logged_in = False

    def _get_session_id(self) -> str:
        """
        Fetch the login page and extract the session ID.

        Returns:
            The session ID (sid) from the login page JavaScript.

        Raises:
            AuthenticationError: If the session ID cannot be extracted.
        """
        url = f"{self.base_url}/cgi-bin/install_login.cgi"

        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        match = self.SID_PATTERN.search(response.text)
        if not match:
            raise AuthenticationError(
                "Could not extract session ID from login page. "
                "The ONT web interface may have changed."
            )

        return match.group(1)

    def _compute_password_hash(self, password: str, sid: str) -> str:
        """
        Compute the MD5 hash for authentication.

        The ONT uses challenge-response: MD5(password + ":" + sid)

        Args:
            password: The plain-text password.
            sid: The session ID from the login page.

        Returns:
            The MD5 hash as a hexadecimal string.
        """
        challenge = f"{password}:{sid}"
        return hashlib.md5(challenge.encode()).hexdigest()

    def login(self, username: str, password: str) -> None:
        """
        Authenticate with the ONT device.

        Args:
            username: The login username.
            password: The login password.

        Raises:
            AuthenticationError: If login fails.
        """
        # Step 1: Get session ID from login page
        sid = self._get_session_id()

        # Step 2: Compute password hash
        password_hash = self._compute_password_hash(password, sid)

        # Step 3: POST login credentials
        url = f"{self.base_url}/cgi-bin/install_login.cgi"
        data = {
            "Loginuser": username,
            "LoginPasswordValue": password_hash,
            "submitValue": "1",
        }

        response = self.session.post(url, data=data, timeout=self.timeout)
        response.raise_for_status()

        # Check if login was successful by looking for error indicators
        # or by trying to access a protected page
        if "Falscher Benutzer oder Passwort" in response.text:
            raise AuthenticationError("Invalid username or password")

        if "Fehler bei Authentifizierung" in response.text:
            raise AuthenticationError("Authentication failed")

        self._logged_in = True

    def fetch_install_info(self) -> str:
        """
        Fetch the install info page HTML.

        Returns:
            The HTML content of the install_info.cgi page.

        Raises:
            RuntimeError: If not logged in.
            requests.HTTPError: If the request fails.
        """
        if not self._logged_in:
            raise RuntimeError("Not logged in. Call login() first.")

        url = f"{self.base_url}/cgi-bin/install_info.cgi"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        # Check if we got redirected to login page
        if "install_login.cgi" in response.text and "window.parent.location" in response.text:
            raise AuthenticationError("Session expired. Please login again.")

        return response.text

    def fetch_identifier(self) -> str:
        """
        Fetch the identifier page HTML (contains connection status).

        Returns:
            The HTML content of the install_identifier.cgi page.

        Raises:
            RuntimeError: If not logged in.
            requests.HTTPError: If the request fails.
        """
        if not self._logged_in:
            raise RuntimeError("Not logged in. Call login() first.")

        url = f"{self.base_url}/cgi-bin/install_identifier.cgi"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        return response.text

    def close(self) -> None:
        """Close the session."""
        self.session.close()

    def __enter__(self) -> "ONTClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
