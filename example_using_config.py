"""
Example script showing how to use the config module.

This demonstrates the recommended way to access VCO credentials
without hardcoding them in the script.
"""

import json
import requests
from config import get_config

# Load configuration from .env file
config = get_config()

# Access configuration values
headers = config['headers']
vco_url = config['vco_url_v1']  # Use vco_url_v2 for API v2
enterprise_id = config['enterprise_id']
verify_ssl = config['verify_ssl']

# Example: Get enterprise edges
get_entEdges = vco_url + 'enterprise/getEnterpriseEdges'

params = {
    "enterpriseId": enterprise_id,
    "with": ["configuration", "links", "site"]
}

response = requests.post(
    get_entEdges,
    headers=headers,
    data=json.dumps(params),
    verify=verify_ssl
)

resp_dict = response.json()

# Write output
with open("example_output.txt", "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"✓ Response saved to example_output.txt")
print(f"  Retrieved {len(resp_dict)} edge(s)")
