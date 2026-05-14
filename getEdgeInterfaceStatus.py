import json
import sys
import asyncio
import requests
import websockets
from config import get_config

########## VCO info and credentials

config = get_config()

token         = config['token']
enterpriseId  = config['enterprise_id']
vco_hostname  = config['vco_hostname']
vco_url       = config['vco_url_v1']
verify_ssl    = config['verify_ssl']
edgeId        = config.get('edge_id')

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods

get_edge      = vco_url + 'edge/getEdge'
ws_url        = f'wss://{vco_hostname}/ws/'

######################### Main Program #####################

if not edgeId:
    print("Error: Edge ID not configured!", file=sys.stderr)
    print("Please run setup_config.py and provide an Edge ID, or set VCO_EDGE_ID in .env", file=sys.stderr)
    sys.exit(1)

# Step 1: Fetch edge logical ID (UUID) — required by the WebSocket API
print(f"Fetching logical ID for edge {edgeId}...")
edge_params = {"id": edgeId, "enterpriseId": enterpriseId}
edge_resp = requests.post(get_edge, headers=headers, data=json.dumps(edge_params), verify=verify_ssl)

if edge_resp.status_code != 200:
    print(f"Error fetching edge: HTTP {edge_resp.status_code}", file=sys.stderr)
    sys.exit(1)

edge_data = edge_resp.json()
edge_logical_id = edge_data.get("logicalId")

if not edge_logical_id:
    print("Error: Could not retrieve edge logicalId", file=sys.stderr)
    sys.exit(1)

print(f"  Edge logical ID: {edge_logical_id}")

# Step 2: Connect via WebSocket and run INTERFACE_STATUS diagnostic
async def run_interface_status():
    # The Authorization header authenticates the initial WebSocket handshake.
    # Upon connection the server sends a noop message containing the session token
    # that must be included in every subsequent message.
    ws_headers = {"Authorization": token}

    ssl_context = None
    if not verify_ssl:
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    print(f"\nConnecting to WebSocket: {ws_url}")
    async with websockets.connect(ws_url, additional_headers=ws_headers, ssl=ssl_context) as ws:

        # Step 3: Receive the noop message — it contains the session token
        noop_raw = await ws.recv()
        noop = json.loads(noop_raw)
        print(f"  Received noop message")

        ws_token = noop.get("token")
        if not ws_token:
            print("Error: No token in noop message", file=sys.stderr)
            print(f"  Noop content: {json.dumps(noop, indent=2)}", file=sys.stderr)
            return None

        # Step 4: Send the INTERFACE_STATUS diagnostic request
        request = {
            "action": "runDiagnostics",
            "token": ws_token,
            "data": {
                "logicalId": edge_logical_id,
                "resformat": "JSON",
                "test": "INTERFACE_STATUS"
            }
        }

        print(f"  Sending INTERFACE_STATUS request...")
        await ws.send(json.dumps(request))

        # Step 5: Receive the response
        response_raw = await ws.recv()
        response = json.loads(response_raw)
        return response

result = asyncio.run(run_interface_status())

if result is None:
    sys.exit(1)

# Step 6: Parse and display results
print(f"\n--- Interface Status for Edge {edgeId} ---\n")

# The output field is a JSON-encoded string — parse it twice
raw_output = result.get("data", {}).get("results", {}).get("output", "")
try:
    parsed = json.loads(raw_output)
    iface_result = parsed.get("INTERFACE_STATUS", {}).get("result", {})
except (json.JSONDecodeError, AttributeError):
    print("Could not parse output — check getEdgeInterfaceStatus.txt for the raw response")
    iface_result = {}

routed    = iface_result.get("routed_interface", [])
switched  = iface_result.get("switch_port", [])

print(f"{'Interface':<12} {'Type':<10} {'MAC Address':<20} {'Link':<8} {'IP Address':<18} {'Speed'}")
print("-" * 85)

for iface in routed:
    name   = iface.get("name", "N/A")
    mac    = iface.get("mac", "N/A")
    link   = iface.get("link_detected", "N/A")
    ip     = iface.get("ip", "N/A")
    speed  = iface.get("speed", "N/A")
    print(f"{name:<12} {'ROUTED':<10} {mac:<20} {link:<8} {ip:<18} {speed}")

for iface in switched:
    name   = iface.get("logical_name", "N/A")
    mac    = iface.get("mac", "N/A")
    link   = iface.get("link_detected", "N/A")
    speed  = iface.get("speed", "N/A")
    print(f"{name:<12} {'SWITCHED':<10} {mac:<20} {link:<8} {'N/A':<18} {speed}")

# Save full response to file
output_file = "getEdgeInterfaceStatus.txt"
with open(output_file, "w") as f:
    f.write(json.dumps(result, indent=2))

print(f"\nFull response saved to {output_file}")
print(f"  Edge ID: {edgeId}")
print(f"  Edge logical ID: {edge_logical_id}")
