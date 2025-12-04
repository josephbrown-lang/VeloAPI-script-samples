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
default_edge_id = config.get('edge_id')  # Get edge_id if set, None otherwise

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods
get_entEdges = vco_url + 'enterprise/getEnterpriseEdges'

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

# Configure edge IDs to query (uses default from config if set)
edgeIds = [default_edge_id] if default_edge_id else []  # Empty list gets all edges

params = {
    "enterpriseId": enterpriseId,
    'edgeIds': edgeIds,
    'with': [
        'configuration'
    ]
}

response = requests.post(get_entEdges, headers=headers, data=json.dumps(params), verify=verify_ssl)

resp_dict = response.json()

# Write output to file
with open("edgeDataExport.txt", "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"✓ Response saved to edgeDataExport.txt")
print(f"  Retrieved data for enterprise ID: {enterpriseId}")
if edgeIds:
    print(f"  Requested edge IDs: {edgeIds}")
else:
    print(f"  Retrieved all edges for enterprise")

######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict, indent=2))


