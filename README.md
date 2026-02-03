# ONT Stats

Fetch and display statistics from MitraStar ONT devices via their web interface.

## Features

- Authenticate with ONT web interface (Challenge-Response with MD5)
- Fetch device information from `/cgi-bin/install_info.cgi`
- Output as JSON or formatted table

## Installation

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package in development mode
pip install -e .

# For development (includes test dependencies)
pip install -e ".[dev]"
```

## Configuration

Create a `credentials.ini` file in the project root:

```ini
[ont]
username = your_username
password = your_password
```

## Usage

```bash
# Activate virtual environment first
source venv/bin/activate
ont-stats

# Or run directly without activating
./venv/bin/ont-stats

# Output as formatted table
ont-stats --format table

# Use custom credentials file
ont-stats --credentials /path/to/credentials.ini

# Specify ONT IP address (default: 192.168.100.1)
ont-stats --host 192.168.100.1
```

## Example Output

```
$ ont-stats --format table
Connecting to http://192.168.100.1...
Logged in successfully
Fetching ONT information...
                  ONT Information
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Field                    ┃ Value                ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ ONT ID                   │ AABBCCDD1122334455EE │
│ Vendor ID                │ MitraStar            │
│ Serial Number            │ 001122334455         │
│ GPON Serial Number       │ MSTC00000000         │
│ MAC Address              │ 00:11:22:33:44:55    │
│ Hardware Version         │ 10                   │
│ Active Software Version  │ FW_v1.0_EXAMPLE      │
│ Standby Software Version │ FW_v0.9_EXAMPLE      │
│ Country Code             │ XX                   │
│ Connection Status        │ Connected            │
│ Optical Power (dBm)      │ -15.00               │
│ Fetched At               │ 2026-02-03 23:54:20  │
└──────────────────────────┴──────────────────────┘
```

## Available Data

The tool fetches the following information from the ONT:

- ONT ID (PLOAM password)
- Vendor ID
- Hardware version
- Active software version
- Standby software version
- Country code
- Serial number
- MAC address
- Optical power (dBm)
- GPON serial number
- Connection status

## Development

```bash
# Run tests
pytest

# Run tests with verbose output
pytest -v
```

## Author

Sascha Ludwig

## License

MIT
