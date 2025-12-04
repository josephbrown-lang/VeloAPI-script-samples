# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains Python sample scripts for interacting with the VMware VeloCloud Orchestrator (VCO) API. The scripts demonstrate various API operations for managing SD-WAN edges, enterprises, metrics, and system properties.

## Architecture

### API Interaction Pattern

All scripts follow a consistent architecture:

1. **Authentication**: Uses token-based authentication with the `Authorization` header
2. **Base URL Construction**:
   - REST API v1: `https://{hostname}/portal/rest/`
   - REST API v2: `https://{hostname}/api/sdwan/v2/`
3. **Request Flow**: Configure headers → Build params → POST/GET request → Write response to file
4. **Output**: All scripts write JSON responses to `.txt` files for inspection

### Two API Versions

The codebase uses two different API versions:

- **REST API v1** (`/portal/rest/`): Used by most scripts (getEdges.py, getEdgev1.py, createToken.py, etc.)
- **REST API v2** (`/api/sdwan/v2/`): Used by getEntEdgesAPIv2.py, uses logical IDs instead of numeric IDs

### Common Configuration Pattern

Each script requires manual configuration of:
- `token`: API authentication token (format: "Token XXX")
- `vco_url`: VCO hostname or IP address
- `enterpriseId` or `enterpriseLogicalID`: Enterprise identifier
- `edgeId`: Edge device identifier (where applicable)

All scripts set `verify=False` to disable SSL certificate verification (suitable for development/testing environments).

## Configuration

### Secure Configuration (Recommended)

Use the provided configuration system to avoid hardcoding credentials:

1. **Run setup script** (first time only):
```bash
python setup_config.py
```
This prompts for your VCO credentials and stores them securely in `.env` (excluded from git).

2. **Install python-dotenv** (optional but recommended):
```bash
pip install python-dotenv
```
Without this, the config module falls back to manual .env parsing.

3. **Use config module in scripts**:
```python
from config import get_config

config = get_config()
headers = config['headers']
vco_url = config['vco_url_v1']  # or vco_url_v2 for API v2
enterprise_id = config['enterprise_id']
verify_ssl = config['verify_ssl']
```

4. **Override values per script**:
```python
config = get_config(enterprise_id=456)  # Override default
```

### Legacy Method (Not Recommended)

Older scripts may have hardcoded values that need manual editing:
- `token = "Token XXX"` → Your actual API token
- `vco_url` hostname (e.g., `vcoXXX.velocloud.net` or IP address)
- `enterpriseId`, `edgeId`, etc. with actual IDs

**Security Note**: Hardcoding credentials is insecure. Use the configuration system above instead.

## Running Scripts

### Prerequisites

```bash
pip install requests
pip install python-dotenv  # Optional, for config system
```

### Execution

1. Configure credentials (first time):
```bash
python setup_config.py
```

2. Run the script:
```bash
python <script_name>.py
```

3. Check the output file generated in the current directory

### Script Categories

**Authentication:**
- `loginTest.py`: Session-based login (uses cookies)
- `createToken.py`: Generate API tokens programmatically

**Enterprise Management:**
- `getEnterpriseIDs.py`: List all enterprises
- `getEnterpriseLogicalID.py`: Get logical ID for an enterprise (needed for API v2)
- `getEnterpriseRouteConfig.py`: Get enterprise routing configuration
- `updateEnterpriseRouteConfig.py`: Update enterprise routing configuration (reads from updateEnterpriseRouteConfig.txt)

**Edge Device Operations:**
- `getEdges.py`: Get enterprise edges with configuration (API v1)
- `getEntEdgesAPIv2.py`: Get enterprise edges using API v2 with logical IDs
- `getEdgev1.py`: Get detailed edge info including links, site, and service groups
- `getEntEdgeLinkStatus.py`: Monitor edge link status across enterprises

**Metrics:**
- `getEdgeLinkSeries.py`: Retrieve time-series data for edge links (requires start/end timestamps in milliseconds)

**System Configuration:**
- `updateWebSocketIP.py`: Update WebSocket server address system property

## Key Implementation Details

### Headers Construction
```python
headers = {"Content-Type": "application/json", "Authorization": token}
```

### Parameter Patterns

Most scripts use the `with` parameter to include additional nested data:
```python
params = {
    "enterpriseId": enterpriseId,
    "with": ["configuration", "links", "site"]
}
```

### Update Scripts Pattern

Update scripts (like `updateEnterpriseRouteConfig.py`) read parameters from JSON files:
- Input file contains all parameters including `enterpriseId`
- Token and VCO URL come from `.env` environment configuration
- Response is written to a separate output file

Example:
```python
# Reads from: updateEnterpriseRouteConfig.txt
# Gets from .env: token, vco_url, verify_ssl
# Writes to: updateEnterpriseRouteConfigResponse.txt
```

### Time Intervals

For metrics queries, timestamps must be in milliseconds since epoch:
```python
"interval": {
    "start": 1748419509417,
    "end": 1748462709417
}
```

### API v2 Differences

API v2 uses GET requests with query parameters and logical IDs:
```python
get_entEdges = vco_url + 'enterprises/' + enterpriseLogicalID + '/edges?include=site.*'
response = requests.get(get_entEdges, headers=headers)
```

## Output Files

Scripts generate the following output files:
- `responseTokenCreate.txt`
- `edgeDataExport.txt`, `edgeData.txt`, `getEdge.txt`
- `getEdgeLinkSeries.txt`
- `getEnterpriseLinkStatus.txt`, `enterpriseList.txt`
- `enterpriseLogicalID.txt`, `enterpriseRouteConfig.txt`
- `updateEnterpriseRouteConfigResponse.txt`
- `response.txt`

## Input Files

Some scripts require input files to define parameters:
- `updateEnterpriseRouteConfig.txt`: Route configuration parameters for updateEnterpriseRouteConfig.py (see .txt.example template)

## Configuration Files

- **setup_config.py**: Interactive script to configure credentials and create `.env` file
- **config.py**: Helper module to load configuration from environment variables
- **.env**: Stores sensitive credentials (created by setup_config.py, excluded from git)
- **.env.example**: Template showing the configuration format
- **.gitignore**: Ensures `.env` and output files are not committed to version control
