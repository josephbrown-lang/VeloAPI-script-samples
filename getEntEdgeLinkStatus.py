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

get_ent_list_status = vco_url + 'monitoring/getEnterpriseEdgeLinkStatus'

params_ent_list = {'links': True, 'detailed': True}

response_ent_list = requests.post(get_ent_list_status, headers=headers, data=json.dumps(params_ent_list), verify=verify_ssl)

resp_dict = response_ent_list.json()

# Write output to file
with open("getEnterpriseLinkStatus.txt", "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"✓ Response saved to getEnterpriseLinkStatus.txt")
if isinstance(resp_dict, list):
    print(f"  Retrieved link status for {len(resp_dict)} enterprise(s)")

