"""Tests for HTML parsing."""

from pathlib import Path

import pytest

from ont_stats.parser import (
    merge_info,
    parse_identifier,
    parse_install_info,
    parse_js_vars,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def install_info_html():
    """Load install_info.html fixture."""
    return (FIXTURES_DIR / "install_info.html").read_text()


@pytest.fixture
def install_identifier_html():
    """Load install_identifier.html fixture."""
    return (FIXTURES_DIR / "install_identifier.html").read_text()


class TestParseJsVars:
    """Tests for parse_js_vars function."""

    def test_parse_gpon_passwd(self):
        """Test extracting gponPasswd variable."""
        html = 'var gponPasswd = "ABC123DEF456";'
        result = parse_js_vars(html)
        assert result["gponPasswd"] == "ABC123DEF456"

    def test_parse_gpon_status(self):
        """Test extracting gponStatus variable."""
        html = 'var gponStatus = "Connected";'
        result = parse_js_vars(html)
        assert result["gponStatus"] == "Connected"

    def test_parse_country_code(self):
        """Test extracting countryCode variable."""
        html = 'var countryCode = "XX";'
        result = parse_js_vars(html)
        assert result["countryCode"] == "XX"

    def test_parse_multiple_vars(self):
        """Test extracting multiple variables."""
        html = '''
        var gponPasswd = "ABC123";
        var gponStatus = "Connected";
        var countryCode = "XX";
        '''
        result = parse_js_vars(html)
        assert result["gponPasswd"] == "ABC123"
        assert result["gponStatus"] == "Connected"
        assert result["countryCode"] == "XX"

    def test_parse_no_vars(self):
        """Test with no matching variables."""
        html = '<html><body>No vars here</body></html>'
        result = parse_js_vars(html)
        assert result == {}


class TestParseInstallInfo:
    """Tests for parse_install_info function."""

    def test_parse_ont_id(self, install_info_html):
        """Test extracting ONT ID from JavaScript."""
        info = parse_install_info(install_info_html)
        assert info.ont_id == "AABBCCDD1122334455EE"

    def test_parse_vendor_id(self, install_info_html):
        """Test extracting vendor ID."""
        info = parse_install_info(install_info_html)
        assert info.vendor_id == "MitraStar"

    def test_parse_hardware_version(self, install_info_html):
        """Test extracting hardware version."""
        info = parse_install_info(install_info_html)
        assert info.hardware_version == "10"

    def test_parse_software_versions(self, install_info_html):
        """Test extracting software versions."""
        info = parse_install_info(install_info_html)
        assert info.active_software_version == "FW_v1.0_EXAMPLE"
        assert info.standby_software_version == "FW_v0.9_EXAMPLE"

    def test_parse_country_code(self, install_info_html):
        """Test extracting country code."""
        info = parse_install_info(install_info_html)
        assert info.country_code == "XX"

    def test_parse_serial_numbers(self, install_info_html):
        """Test extracting serial numbers."""
        info = parse_install_info(install_info_html)
        assert info.serial_number == "001122334455"
        assert info.gpon_serial_number == "MSTC00000000"

    def test_parse_mac_address(self, install_info_html):
        """Test extracting MAC address."""
        info = parse_install_info(install_info_html)
        assert info.mac_address == "00:11:22:33:44:55"

    def test_parse_optical_power(self, install_info_html):
        """Test extracting optical power."""
        info = parse_install_info(install_info_html)
        assert info.optical_power_dbm == "-12.34"

    def test_to_dict(self, install_info_html):
        """Test conversion to dictionary."""
        info = parse_install_info(install_info_html)
        result = info.to_dict()

        assert result["ont_id"] == "AABBCCDD1122334455EE"
        assert result["vendor_id"] == "MitraStar"
        assert "fetched_at" in result


class TestParseIdentifier:
    """Tests for parse_identifier function."""

    def test_parse_connection_status(self, install_identifier_html):
        """Test extracting connection status."""
        result = parse_identifier(install_identifier_html)
        assert result["connection_status"] == "Connected"

    def test_parse_country_code(self, install_identifier_html):
        """Test extracting country code."""
        result = parse_identifier(install_identifier_html)
        assert result["country_code"] == "XX"

    def test_parse_ont_id(self, install_identifier_html):
        """Test extracting ONT ID."""
        result = parse_identifier(install_identifier_html)
        assert result["ont_id"] == "AABBCCDD1122334455EE"


class TestMergeInfo:
    """Tests for merge_info function."""

    def test_merge_connection_status(self, install_info_html, install_identifier_html):
        """Test merging connection status."""
        info = parse_install_info(install_info_html)
        identifier_data = parse_identifier(install_identifier_html)

        merged = merge_info(info, identifier_data)

        assert merged.connection_status == "Connected"

    def test_merge_preserves_existing(self, install_info_html, install_identifier_html):
        """Test that merge preserves existing values."""
        info = parse_install_info(install_info_html)
        identifier_data = parse_identifier(install_identifier_html)

        merged = merge_info(info, identifier_data)

        # Original values should be preserved
        assert merged.vendor_id == "MitraStar"
        assert merged.serial_number == "001122334455"
