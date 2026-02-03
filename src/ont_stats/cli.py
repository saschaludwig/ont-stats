"""Command-line interface for ONT Stats."""

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .client import AuthenticationError, ONTClient
from .config import ConfigError, load_credentials
from .models import ONTInfo
from .parser import merge_info, parse_identifier, parse_install_info


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="ont-stats",
        description="Fetch statistics from MitraStar ONT devices",
    )

    parser.add_argument(
        "--credentials",
        "-c",
        type=Path,
        default=Path("credentials.ini"),
        help="Path to credentials INI file (default: credentials.ini)",
    )

    parser.add_argument(
        "--host",
        "-H",
        type=str,
        default=None,
        help="ONT IP address (default: 192.168.100.1)",
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "table"],
        default="json",
        help="Output format (default: json)",
    )

    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)",
    )

    return parser


def print_table(info: ONTInfo, console: Console) -> None:
    """Print ONT info as a formatted table."""
    table = Table(title="ONT Information", show_header=True, header_style="bold cyan")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    # Add rows for each field
    table.add_row("ONT ID", info.ont_id or "-")
    table.add_row("Vendor ID", info.vendor_id or "-")
    table.add_row("Serial Number", info.serial_number or "-")
    table.add_row("GPON Serial Number", info.gpon_serial_number or "-")
    table.add_row("MAC Address", info.mac_address or "-")
    table.add_row("Hardware Version", info.hardware_version or "-")
    table.add_row("Active Software Version", info.active_software_version or "-")
    table.add_row("Standby Software Version", info.standby_software_version or "-")
    table.add_row("Country Code", info.country_code or "-")
    table.add_row("Connection Status", info.connection_status or "-")
    table.add_row("Optical Power (dBm)", info.optical_power_dbm or "-")
    table.add_row("Fetched At", info.fetched_at.strftime("%Y-%m-%d %H:%M:%S"))

    # Add extra fields if any
    for key, value in info.extra_fields.items():
        table.add_row(key.replace("_", " ").title(), value)

    console.print(table)


def print_json(info: ONTInfo) -> None:
    """Print ONT info as JSON."""
    print(json.dumps(info.to_dict(), indent=2))


def fetch_ont_info(client: ONTClient) -> ONTInfo:
    """Fetch and parse ONT information."""
    # Fetch and parse install_info page
    info_html = client.fetch_install_info()
    info = parse_install_info(info_html)

    # Fetch and merge identifier page for connection status
    try:
        identifier_html = client.fetch_identifier()
        identifier_data = parse_identifier(identifier_html)
        info = merge_info(info, identifier_data)
    except Exception:
        # Identifier page is optional, don't fail if it's unavailable
        pass

    return info


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    console = Console(stderr=True)

    # Load credentials
    try:
        username, password = load_credentials(args.credentials)
    except ConfigError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        return 1

    # Connect to ONT
    try:
        with ONTClient(host=args.host, timeout=args.timeout) as client:
            # Authenticate
            console.print(f"[dim]Connecting to {client.base_url}...[/dim]")
            client.login(username, password)
            console.print("[green]Logged in successfully[/green]")

            # Fetch data
            console.print("[dim]Fetching ONT information...[/dim]")
            info = fetch_ont_info(client)

            # Output
            if args.format == "table":
                # Print table to stdout (use a new console for stdout)
                output_console = Console()
                print_table(info, output_console)
            else:
                print_json(info)

    except AuthenticationError as e:
        console.print(f"[red]Authentication failed:[/red] {e}")
        return 1
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
