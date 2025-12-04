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

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods
update_route_config = vco_url + 'enterprise/updateEnterpriseRouteConfiguration'

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

# Read parameters from updateEnterpriseRouteConfig.txt
params_file = "updateEnterpriseRouteConfig.txt"

if not os.path.exists(params_file):
    print(f"Error: {params_file} not found!", file=sys.stderr)
    print(f"Please create {params_file} with the route configuration parameters.", file=sys.stderr)
    print("\nExample format:")
    print('{')
    print('  "enterpriseId": 123,')
    print('  "_update": {')
    print('    "data": [')
    print('      {')
    print('        "routes": [...],')
    print('        ...')
    print('      }')
    print('    ]')
    print('  }')
    print('}')
    sys.exit(1)

try:
    with open(params_file, 'r') as f:
        params = json.load(f)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON in {params_file}: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error reading {params_file}: {e}", file=sys.stderr)
    sys.exit(1)

# Validate required fields
if "enterpriseId" not in params:
    print(f"Error: 'enterpriseId' not found in {params_file}", file=sys.stderr)
    sys.exit(1)

enterpriseId = params["enterpriseId"]

print(f"Updating enterprise route configuration...")
print(f"  Enterprise ID: {enterpriseId}")
print(f"  Reading parameters from: {params_file}")

response = requests.post(update_route_config, headers=headers, data=json.dumps(params), verify=verify_ssl)

resp_dict = response.json()

# Write output to file
output_file = "updateEnterpriseRouteConfigResponse.txt"
with open(output_file, "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"\n✓ Update request completed")
print(f"  Response saved to {output_file}")
print(f"  HTTP Status: {response.status_code}")

# Check for success/error in response
if response.status_code == 200:
    print(f"  Status: Success")
else:
    print(f"  Status: Check response file for details")

######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict, indent=2))
