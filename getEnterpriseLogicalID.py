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
get_Enterprise = vco_url + 'enterprise/getEnterprise'

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

params = {
    "enterpriseId": enterpriseId
}

response = requests.post(get_Enterprise, headers=headers, data=json.dumps(params), verify=verify_ssl)

resp_dict = response.json()

entLogicalId = resp_dict.get("logicalId", "Not found")

# Write output to file
with open("enterpriseLogicalID.txt", "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"✓ Response saved to enterpriseLogicalID.txt")
print(f"  Enterprise ID: {enterpriseId}")
print(f"  Enterprise Logical ID: {entLogicalId}")

######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict, indent=2))


