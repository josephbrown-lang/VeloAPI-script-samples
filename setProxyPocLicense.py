import json
import os
import sys
import requests
from config import get_config

########## VCO info and credentials

# Load configuration from .env file
config = get_config()

# Get values from config
token      = config['token']
vco_url    = config['vco_url_v1']
verify_ssl = config['verify_ssl']

# Enterprise proxy (partner) ID — set VCO_ENTERPRISE_PROXY_ID in .env
# or edit the value directly below.
enterpriseProxyId = os.getenv('VCO_ENTERPRISE_PROXY_ID')
if enterpriseProxyId:
    try:
        enterpriseProxyId = int(enterpriseProxyId)
    except ValueError:
        print(f"Error: VCO_ENTERPRISE_PROXY_ID must be numeric, got '{enterpriseProxyId}'", file=sys.stderr)
        sys.exit(1)
else:
    print("Error: Enterprise proxy ID not configured!", file=sys.stderr)
    print("Add VCO_ENTERPRISE_PROXY_ID=<id> to your .env file, or set it before running:", file=sys.stderr)
    print("  VCO_ENTERPRISE_PROXY_ID=62 python3 setProxyPocLicense.py", file=sys.stderr)
    sys.exit(1)

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods

get_proxy_licenses      = vco_url + 'license/getEnterpriseProxyEdgeLicenses'
add_licenses_to_proxy   = vco_url + 'license/addEdgeLicensesToEnterpriseProxy'
update_proxy_licenses   = vco_url + 'license/updateEnterpriseProxyEdgeLicenses'

# POC license ID to assign to the proxy
POC_LICENSE_ID = 325

######################### Main Program #####################
#### MAIN BODY
######################### Main Program #####################

# Step 1: Show current proxy license assignments with counts
# edgeCount   = edges consuming this license under the proxy
# enterpriseCount = enterprises under the proxy that have this license assigned
print(f"Fetching current license assignments for proxy {enterpriseProxyId}...")
current_params = {
    "enterpriseProxyId": enterpriseProxyId,
    "with": ["counts"]
}
current_resp = requests.post(get_proxy_licenses, headers=headers,
                             data=json.dumps(current_params), verify=verify_ssl)

if current_resp.status_code != 200:
    print(f"Error fetching proxy licenses: HTTP {current_resp.status_code}", file=sys.stderr)
    sys.exit(1)

current_licenses = current_resp.json()

in_use = []
safe_to_remove = []

if current_licenses:
    print(f"\n  Current proxy license assignments ({len(current_licenses)} licenses):")
    print(f"  {'ID':<6} {'Edition':<14} {'Bandwidth':<10} {'Edges':<7} {'Enterprises':<12} {'SKU'}")
    print("  " + "-" * 80)
    for lic in current_licenses:
        edge_count = lic.get('edgeCount', 0)
        ent_count  = lic.get('enterpriseCount', 0)
        marker = " ← in use" if (edge_count > 0 or ent_count > 0) else ""
        print(f"  {lic.get('id', 'N/A'):<6} "
              f"{lic.get('edition', 'N/A'):<14} "
              f"{lic.get('bandwidthTier', 'N/A'):<10} "
              f"{edge_count:<7} "
              f"{ent_count:<12} "
              f"{lic.get('sku', 'N/A')}{marker}")
        if edge_count > 0 or ent_count > 0:
            in_use.append(lic['id'])
        elif lic['id'] != POC_LICENSE_ID:
            safe_to_remove.append(lic['id'])
else:
    print("  No licenses currently assigned to this proxy.")

# Step 2: Add POC license 325 directly to the proxy.
# addEdgeLicensesToEnterpriseProxy inserts the association without removing
# existing licenses, bypassing the edgeCount/enterpriseCount guard entirely.
# This is the correct approach when existing licenses are still in use.
print(f"\nAdding POC license {POC_LICENSE_ID} to proxy {enterpriseProxyId}...")

add_params = {
    "enterpriseProxyId": enterpriseProxyId,
    "ids": [POC_LICENSE_ID]
}

add_resp = requests.post(add_licenses_to_proxy, headers=headers,
                         data=json.dumps(add_params), verify=verify_ssl)

add_result = add_resp.json()

output_file = "setProxyPocLicense.txt"
with open(output_file, "w") as f:
    f.write(json.dumps(add_result, indent=2))

print(f"\n✓ Response saved to {output_file}")
print(f"  Proxy ID    : {enterpriseProxyId}")
print(f"  HTTP Status : {add_resp.status_code}")

if add_resp.status_code == 200:
    print(f"  Status: POC license {POC_LICENSE_ID} added to proxy successfully.")

    if in_use:
        print(f"\n  Note: {len(in_use)} existing license(s) are still in use and were NOT removed:")
        print(f"  IDs: {in_use}")
        print(f"  To make POC the only license on this proxy, all enterprises/edges under")
        print(f"  the proxy must be migrated off those licenses first, then call")
        print(f"  updateEnterpriseProxyEdgeLicenses with ids:[{POC_LICENSE_ID}].")

    if safe_to_remove:
        # Step 3: Clean up unused licenses (optional — only those with no edges/enterprises)
        print(f"\n  {len(safe_to_remove)} unused license(s) can be removed now: IDs {safe_to_remove}")
        print(f"  Running cleanup...")
        cleanup_params = {
            "enterpriseProxyId": enterpriseProxyId,
            "ids": [POC_LICENSE_ID]  # keep only POC, let update remove the unused ones
        }
        # Build the full desired set: POC + any that are still in use
        keep_ids = [POC_LICENSE_ID] + in_use
        cleanup_params["ids"] = keep_ids
        cleanup_resp = requests.post(update_proxy_licenses, headers=headers,
                                     data=json.dumps(cleanup_params), verify=verify_ssl)
        cleanup_result = cleanup_resp.json()
        with open(output_file, "w") as f:
            f.write(json.dumps(cleanup_result, indent=2))
        if cleanup_resp.status_code == 200 and cleanup_result.get("valid"):
            print(f"  Cleanup complete — unused licenses removed.")
        else:
            print(f"  Cleanup response: {cleanup_result}")
else:
    print(f"  HTTP {add_resp.status_code} — check {output_file} for error details.")

######## Debugging

#print(add_resp.json())
#print("response is ", json.dumps(add_result, indent=2))
