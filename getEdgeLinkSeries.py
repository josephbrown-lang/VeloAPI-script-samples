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
get_edgeLinkSeries = vco_url + 'metrics/getEdgeLinkSeries'

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

# Check if edge ID is configured
if not edgeId:
    print("Error: Edge ID not configured!", file=sys.stderr)
    print("Please run setup_config.py and provide an Edge ID, or set VCO_EDGE_ID in .env", file=sys.stderr)
    sys.exit(1)

# Configure time interval (update start/end timestamps as needed)
# Timestamps must be in milliseconds since epoch
interval_start = 1748419509417  # Replace with your start timestamp
interval_end = 1748462709417    # Replace with your end timestamp

params = {
    "edgeId": edgeId,
    "enterpriseId": enterpriseId,
    "interval": {
        "start": interval_start,
        "end": interval_end
    }
}

response = requests.post(get_edgeLinkSeries, headers=headers, data=json.dumps(params), verify=verify_ssl)

resp_dict = response.json()

# Write output to file
with open("getEdgeLinkSeries.txt", "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"✓ Response saved to getEdgeLinkSeries.txt")
print(f"  Edge ID: {edgeId}")
print(f"  Enterprise ID: {enterpriseId}")
print(f"  Interval: {interval_start} to {interval_end}")

######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict, indent=2))


