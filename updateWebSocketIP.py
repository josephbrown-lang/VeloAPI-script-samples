import ssl
import argparse
import json
import os
import sys
from copy import deepcopy
import requests
from config import get_config

########## VCO info and credentials

# Load configuration from .env file
config = get_config()

# Get values from config
token = config['token']
vco_url = config['vco_url_v1']
verify_ssl = config['verify_ssl']

# Configure WebSocket IP address (update as needed)
publicIP = "XXX.X.X.X"  # Replace with your WebSocket server IP address

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods
updateSystemProperty = vco_url + 'systemProperty/updateSystemProperty'

# Validate publicIP is configured
if publicIP == "XXX.X.X.X":
    print("Error: WebSocket IP address not configured!", file=sys.stderr)
    print("Please edit this script and set publicIP to your WebSocket server IP address", file=sys.stderr)
    sys.exit(1)

params = {
    "id": 471,
    "_update": {
        "name": "network.portal.websocket.address",
        "dataType": "STRING",
        "isPassword": 0,
        "isReadOnly": 0,
        "description": "address of the realtime server for websocket requests from the browser",
        "value": publicIP
    }
}

print(f"Updating WebSocket server address...")
print(f"  New address: {publicIP}")

response = requests.post(updateSystemProperty, headers=headers, data=json.dumps(params), verify=verify_ssl)

resp_dict = response.json()

# Write output to file
output_file = "updateWebSocketResponse.txt"
with open(output_file, "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"\n✓ Update request completed")
print(f"  Response saved to {output_file}")
print(f"  HTTP Status: {response.status_code}")


