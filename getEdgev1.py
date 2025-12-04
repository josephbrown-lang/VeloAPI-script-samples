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
enterpriseId = config['enterprise_id']
vco_url = config['vco_url_v1']
verify_ssl = config['verify_ssl']
edgeId = config.get('edge_id')  # Get edge_id if set, None otherwise

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods
get_Edges = vco_url + 'edge/getEdge'



######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

# Check if edge ID is configured
if not edgeId:
    print("Error: Edge ID not configured!", file=sys.stderr)
    print("Please run setup_config.py and provide an Edge ID, or set VCO_EDGE_ID in .env", file=sys.stderr)
    sys.exit(1)

params = {
    "id": edgeId,
    "enterpriseId": enterpriseId,
    "with": [
        "links",
        "recentLinks",
        "site",
        "serviceGroups",
        "configuration"
    ]
}

response = requests.post(get_Edges, headers=headers, data=json.dumps(params), verify=verify_ssl)

resp_dict = response.json()

# Write output to file
with open("getEdge.txt", "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"✓ Response saved to getEdge.txt")
print(f"  Retrieved data for edge ID: {edgeId}")
print(f"  Enterprise ID: {enterpriseId}")

######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict, indent=2))


