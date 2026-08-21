import json
import sys
import requests
from config import get_config

########## VCO info and credentials

# Load configuration from .env file
config = get_config()

# Get values from config
token        = config['token']
enterpriseId = config['enterprise_id']
vco_url      = config['vco_url_v1']
verify_ssl   = config['verify_ssl']

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods

get_enterprise_licenses     = vco_url + 'license/getEnterpriseEdgeLicenses'
get_network_licenses        = vco_url + 'license/getNetworkEdgeLicenses'
add_licenses_to_enterprise  = vco_url + 'license/addEdgeLicensesToEnterprise'
set_enterprise_lic_edition  = vco_url + 'license/setEnterpriseEdgeLicenseEdition'

# POC license ID available on this VCO — used for reference/verification only.
# setEnterpriseEdgeLicenseEdition selects the appropriate POC license automatically
# based on bandwidth tier matching; it does not accept a specific license ID.
POC_LICENSE_ID = 325

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

if not enterpriseId:
    print("Error: Enterprise ID not configured!", file=sys.stderr)
    print("Please run setup_config.py and provide an Enterprise ID, or set VCO_ENTERPRISE_ID in .env", file=sys.stderr)
    sys.exit(1)

# Step 1: Show current enterprise licenses (with edge assignment counts)
print(f"Fetching current license assignments for enterprise {enterpriseId}...")
current_params = {
    "enterpriseId": enterpriseId,
    "with": ["counts"]
}
current_resp = requests.post(get_enterprise_licenses, headers=headers,
                             data=json.dumps(current_params), verify=verify_ssl)

if current_resp.status_code != 200:
    print(f"Error fetching current licenses: HTTP {current_resp.status_code}", file=sys.stderr)
    sys.exit(1)

current_licenses = current_resp.json()

if current_licenses:
    print(f"\n  Current license assignments ({len(current_licenses)} licenses):")
    print(f"  {'ID':<6} {'Edition':<14} {'Bandwidth':<10} {'Edges':<6} {'SKU'}")
    print("  " + "-" * 72)
    for lic in current_licenses:
        print(f"  {lic.get('id', 'N/A'):<6} "
              f"{lic.get('edition', 'N/A'):<14} "
              f"{lic.get('bandwidthTier', 'N/A'):<10} "
              f"{lic.get('edgeCount', 0):<6} "
              f"{lic.get('sku', 'N/A')}")
else:
    print("  No licenses currently assigned.")

# Step 2: Check what POC licenses are available at the network level
print(f"\nChecking network-level POC license availability...")
net_resp = requests.post(get_network_licenses, headers=headers,
                         data=json.dumps({"edition": "POC"}), verify=verify_ssl)

network_poc_licenses = net_resp.json() if net_resp.status_code == 200 else []

if isinstance(network_poc_licenses, list) and network_poc_licenses:
    print(f"  Found {len(network_poc_licenses)} POC license(s) at network level:")
    for lic in network_poc_licenses:
        print(f"    ID {lic.get('id'):<6} {lic.get('bandwidthTier','N/A'):<10} {lic.get('sku','N/A')}")
else:
    print(f"  No POC licenses found at network level.")
    print(f"  setEnterpriseEdgeLicenseEdition requires POC licenses to be pre-configured")
    print(f"  at the operator/network level — trying direct assignment of license {POC_LICENSE_ID} instead.")

# Step 3: Assign POC license directly to the enterprise.
# addEdgeLicensesToEnterprise adds the license without removing existing ones,
# bypassing the edgeCount check. Use this when setEnterpriseEdgeLicenseEdition
# returns [] due to no matching POC licenses at the network level.
print(f"\nAdding POC license {POC_LICENSE_ID} directly to enterprise {enterpriseId}...")

add_params = {
    "enterpriseId": enterpriseId,
    "ids": [POC_LICENSE_ID]
}

response = requests.post(add_licenses_to_enterprise, headers=headers,
                         data=json.dumps(add_params), verify=verify_ssl)

resp_dict = response.json()

# Write full response to file
output_file = "setEnterprisePocLicense.txt"
with open(output_file, "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"\n✓ Response saved to {output_file}")
print(f"  Enterprise ID : {enterpriseId}")
print(f"  HTTP Status   : {response.status_code}")

if response.status_code == 200:
    if resp_dict is None or resp_dict == {} or resp_dict == []:
        print(f"  Status: License {POC_LICENSE_ID} added successfully.")
        print(f"  Note: Enterprise now has both the existing license and POC license assigned.")
        print(f"  To make POC the only license, first unassign edges from the existing license,")
        print(f"  then call updateEnterpriseEdgeLicenses with ids:[{POC_LICENSE_ID}].")
    elif isinstance(resp_dict, dict) and resp_dict.get("error"):
        print(f"  Error: {resp_dict['error']}")
    else:
        print(f"  Response: {resp_dict}")
else:
    print(f"  HTTP {response.status_code} — check {output_file} for error details.")

######## Debugging

#print(response.json())
#print("response is ", json.dumps(resp_dict, indent=2))
