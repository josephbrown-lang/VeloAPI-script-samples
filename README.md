# VeloCloud SD-WAN API Sample Scripts

Python scripts demonstrating VeloCloud Orchestrator (VCO) API usage for managing and monitoring SD-WAN edges, enterprises, metrics, and diagnostics.

## Prerequisites

### Python

Python 3.7 or newer is required.

### Required packages

```bash
pip install requests websockets
```

| Package | Used by | Purpose |
|---|---|---|
| `requests` | All scripts except `getEdgeInterfaceStatus.py` | HTTPS REST API calls to VCO |
| `websockets` | `getEdgeInterfaceStatus.py` | WebSocket connection for Remote Diagnostics API |

### Optional package

```bash
pip install python-dotenv
```

`python-dotenv` is used by `config.py` to load credentials from the `.env` file. Without it, the config module falls back to a built-in `.env` parser that covers all basic cases — install it only if you encounter parsing issues with quoted or multi-line values.

## Setup

Run the interactive setup script once before using any other script:

```bash
python setup_config.py
```

This prompts for your VCO hostname, API token, and optional enterprise/edge IDs, then writes them to a `.env` file (excluded from git).

To configure manually, create a `.env` file in this directory:

```
VCO_HOSTNAME=your-vco-hostname.example.com
VCO_TOKEN=Token your-api-token-here
VCO_ENTERPRISE_ID=12345
VCO_ENTERPRISE_LOGICAL_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
VCO_EDGE_ID=67890
VCO_VERIFY_SSL=false
```

## Scripts

### Authentication

| Script | Description |
|---|---|
| `setup_config.py` | Interactive setup — creates `.env` with your VCO credentials |
| `loginTest.py` | Session-based login test using cookies |
| `createToken.py` | Generate a VCO API token programmatically |

### Enterprise & Edge

| Script | Description |
|---|---|
| `getEnterpriseIDs.py` | List all enterprises and their numeric IDs |
| `getEnterpriseLogicalID.py` | Get the logical ID (UUID) for an enterprise — required for API v2 |
| `getEdges.py` | List all edges for an enterprise with configuration (API v1) |
| `getEdgev1.py` | Get detailed edge info including links, site, and service groups (API v1) |
| `getEntEdgesAPIv2.py` | List enterprise edges using API v2 (uses logical IDs) |

### Metrics

| Script | Description |
|---|---|
| `getEdgeNetworkInterfaceMetrics.py` | Aggregate interface metrics for the past hour. Returns routed interfaces only — switched LAN interfaces are excluded by the edge |
| `getEdgeLinkSeries.py` | Time-series WAN link metrics for a specified interval |

### Monitoring & Status

| Script | Description |
|---|---|
| `getEntEdgeLinkStatus.py` | WAN link status (STABLE/UNSTABLE/DISCONNECTED) across all enterprise edges |
| `getEdgeInterfaceStatus.py` | Physical interface status (MAC address, up/down) via the Remote Diagnostics WebSocket API. Covers all interface types including switched LAN |

### Configuration

| Script | Description |
|---|---|
| `getEnterpriseRouteConfig.py` | Get enterprise routing configuration |
| `updateEnterpriseRouteConfig.py` | Update enterprise routing configuration (reads parameters from `updateEnterpriseRouteConfig.txt`) |
| `updateWebSocketIP.py` | Update the WebSocket server address system property on VCO |

## API versions

| Version | Base URL | Identifiers |
|---|---|---|
| REST v1 | `https://{hostname}/portal/rest/` | Numeric IDs (`edgeId`, `enterpriseId`) |
| REST v2 | `https://{hostname}/api/sdwan/v2/` | Logical IDs (UUIDs) |
| WebSocket | `wss://{hostname}/ws/` | Edge logical ID (UUID) |

The WebSocket API (Remote Diagnostics) requires edge software version 5.0.0 or newer.

## Output files

Scripts write JSON responses to `.txt` files in the current directory:

```
edgeDataExport.txt
enterpriseList.txt
enterpriseLogicalID.txt
enterpriseRouteConfig.txt
getEdgeInterfaceStatus.txt
getEdgeLinkSeries.txt
getEdgeNetworkInterfaceMetrics.txt
getEnterpriseLinkStatus.txt
updateEnterpriseRouteConfigResponse.txt
```

## Notes

- SSL verification is disabled by default (`VCO_VERIFY_SSL=false`) for compatibility with self-signed VCO certificates. Set to `true` in production environments where the VCO certificate is trusted.
- `getEdgeInterfaceStatus.py` makes a REST call first to resolve the numeric edge ID to a logical ID (UUID), then opens the WebSocket connection.
- `updateEnterpriseRouteConfig.py` reads its full parameter payload from `updateEnterpriseRouteConfig.txt`. See `updateEnterpriseRouteConfig.txt.example` for the expected format.
