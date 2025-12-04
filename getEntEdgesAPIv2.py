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
enterpriseLogicalID = config.get('enterprise_logical_id', 'XXX')  # Falls back to XXX if not set
vco_url = config['vco_url_v2']  # API v2
verify_ssl = config['verify_ssl']

headers = {"Content-Type": "application/json", "Authorization": token}


######## VCO API methods

get_entEdges = vco_url + 'enterprises/' + enterpriseLogicalID + '/edges?include=site.*'


######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

response = requests.get(get_entEdges, headers=headers, verify=verify_ssl)

resp_dict = response.json()

# Write output to file
with open("edgeData.txt", "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"✓ Response saved to edgeData.txt")
print(f"  Enterprise Logical ID: {enterpriseLogicalID}")
if 'data' in resp_dict and isinstance(resp_dict['data'], list):
    print(f"  Retrieved {len(resp_dict['data'])} edge(s)")

######## Debugging

#respData=resp_dict["data"][5]
#respSite=respData["site"]

#print(respSite)

#print(get_entEdges)