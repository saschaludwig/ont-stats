"""Data models for ONT Stats."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ONTInfo:
    """Information fetched from the ONT device."""

    # Core identification
    ont_id: str = ""
    vendor_id: str = ""
    serial_number: str = ""
    gpon_serial_number: str = ""
    mac_address: str = ""

    # Version information
    hardware_version: str = ""
    active_software_version: str = ""
    standby_software_version: str = ""

    # Status
    country_code: str = ""
    connection_status: str = ""
    optical_power_dbm: str = ""

    # Metadata
    fetched_at: datetime = field(default_factory=datetime.now)

    # Additional fields not explicitly defined
    extra_fields: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "ont_id": self.ont_id,
            "vendor_id": self.vendor_id,
            "serial_number": self.serial_number,
            "gpon_serial_number": self.gpon_serial_number,
            "mac_address": self.mac_address,
            "hardware_version": self.hardware_version,
            "active_software_version": self.active_software_version,
            "standby_software_version": self.standby_software_version,
            "country_code": self.country_code,
            "connection_status": self.connection_status,
            "optical_power_dbm": self.optical_power_dbm,
            "fetched_at": self.fetched_at.isoformat(),
        }

        if self.extra_fields:
            result["extra_fields"] = self.extra_fields

        return result
