"""HTML parsing for ONT device pages."""

import re
from datetime import datetime

from bs4 import BeautifulSoup

from .models import ONTInfo


# Regex patterns for JavaScript variables
JS_VAR_PATTERNS = {
    "gponPasswd": re.compile(r'var\s+gponPasswd\s*=\s*"([^"]*)"'),
    "gponStatus": re.compile(r'var\s+gponStatus\s*=\s*"([^"]*)"'),
    "countryCode": re.compile(r'var\s+countryCode\s*=\s*"([^"]*)"'),
}

# Mapping from German labels to ONTInfo field names
LABEL_FIELD_MAP = {
    "Aktuelle ONT ID": "ont_id",
    "Händler ID": "vendor_id",
    "Hardwareversion": "hardware_version",
    "Aktive Softwareversion": "active_software_version",
    "Standby Softwareversion": "standby_software_version",
    "Landesvorwahl": "country_code",
    "Seriennummer": "serial_number",
    "MAC-Adresse": "mac_address",
    "Optische Leistung (dBm)": "optical_power_dbm",
    "GPON-Seriennummer": "gpon_serial_number",
}


def parse_js_vars(html: str) -> dict[str, str]:
    """
    Extract JavaScript variable values from HTML.

    Args:
        html: The HTML content to parse.

    Returns:
        Dictionary of variable names to their values.
    """
    result = {}

    for var_name, pattern in JS_VAR_PATTERNS.items():
        match = pattern.search(html)
        if match:
            result[var_name] = match.group(1)

    return result


def parse_install_info(html: str) -> ONTInfo:
    """
    Parse the install_info.cgi page and extract ONT information.

    Args:
        html: The HTML content of the install_info.cgi page.

    Returns:
        ONTInfo object with parsed data.
    """
    soup = BeautifulSoup(html, "lxml")
    info = ONTInfo(fetched_at=datetime.now())

    # Extract values from JavaScript variables (for ONT ID)
    js_vars = parse_js_vars(html)
    if "gponPasswd" in js_vars:
        info.ont_id = js_vars["gponPasswd"]

    # Extract values from form inputs
    # The structure is: <label>Field Name</label> ... <input value="...">
    form_groups = soup.find_all("div", class_="form-group")

    for group in form_groups:
        label = group.find("label")
        if not label:
            continue

        label_text = label.get_text(strip=True)

        # Find the input in the same form-group
        input_elem = group.find("input", {"readonly": "readonly"})
        if not input_elem:
            continue

        value = input_elem.get("value", "")

        # Map to field name - only set if value is not empty
        field_name = LABEL_FIELD_MAP.get(label_text)

        if field_name and value:
            setattr(info, field_name, value)
        elif label_text and value and not field_name:
            # Store unknown fields in extra_fields
            key = label_text.lower().replace(" ", "_").replace("-", "_")
            info.extra_fields[key] = value

    return info


def parse_identifier(html: str) -> dict[str, str]:
    """
    Parse the install_identifier.cgi page for connection status.

    Args:
        html: The HTML content of the install_identifier.cgi page.

    Returns:
        Dictionary with connection status information.
    """
    result = {}

    js_vars = parse_js_vars(html)

    if "gponStatus" in js_vars:
        result["connection_status"] = js_vars["gponStatus"]

    if "countryCode" in js_vars:
        result["country_code"] = js_vars["countryCode"]

    if "gponPasswd" in js_vars:
        result["ont_id"] = js_vars["gponPasswd"]

    return result


def merge_info(info: ONTInfo, identifier_data: dict[str, str]) -> ONTInfo:
    """
    Merge identifier page data into ONTInfo.

    Args:
        info: The ONTInfo object to update.
        identifier_data: Data from parse_identifier().

    Returns:
        The updated ONTInfo object.
    """
    if "connection_status" in identifier_data:
        info.connection_status = identifier_data["connection_status"]

    # Only update if not already set
    if not info.country_code and "country_code" in identifier_data:
        info.country_code = identifier_data["country_code"]

    if not info.ont_id and "ont_id" in identifier_data:
        info.ont_id = identifier_data["ont_id"]

    return info
