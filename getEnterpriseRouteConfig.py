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

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods
get_route_config = vco_url + 'enterprise/getEnterpriseRouteConfiguration'

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

params = {
    "enterpriseId": enterpriseId
}

response = requests.post(get_route_config, headers=headers, data=json.dumps(params), verify=verify_ssl)

resp_dict = response.json()

# Write output to file
with open("enterpriseRouteConfig.txt", "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"✓ Response saved to enterpriseRouteConfig.txt")
print(f"  Retrieved route configuration for enterprise ID: {enterpriseId}")

######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict, indent=2))
