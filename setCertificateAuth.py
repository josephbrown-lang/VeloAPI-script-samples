import json
import sys
import requests
from config import get_config

########## VCO Configuration

config = get_config()

token = config['token']
vco_url = config['vco_url_v1']
verify_ssl = config['verify_ssl']
enterprise_id = config.get('enterprise_id')

headers = config['headers']

######## VCO API Methods

get_enterprise = vco_url + 'enterprise/getEnterprise'
get_enterprise_edges = vco_url + 'enterprise/getEnterpriseEdges'
update_edge_attributes = vco_url + 'edge/updateEdgeAttributes'

######## Configuration

TARGET_PKI_MODE = "CERTIFICATE_REQUIRED"

######################### Main Program #####################

# Parse flags
dry_run = '--dry-run' in sys.argv
auto_yes = '--yes' in sys.argv

if not enterprise_id:
    print("Error: Enterprise ID not configured!", file=sys.stderr)
    print("Please run setup_config.py", file=sys.stderr)
    sys.exit(1)

# Step 1: Fetch enterprise info
print(f"Fetching enterprise {enterprise_id}...")
params = {"id": enterprise_id}
response = requests.post(get_enterprise, headers=headers, data=json.dumps(params), verify=verify_ssl)

if response.status_code != 200:
    print(f"Error: Failed to fetch enterprise (HTTP {response.status_code})", file=sys.stderr)
    sys.exit(1)

enterprise = response.json()
enterprise_name = enterprise.get("name", "Unknown")
print(f"Enterprise: {enterprise_name} (ID: {enterprise_id})")

# Step 2: Fetch all edges with certificate info
print(f"\nFetching edges...")
params = {
    "enterpriseId": enterprise_id,
    "with": ["certificates"]
}
response = requests.post(get_enterprise_edges, headers=headers, data=json.dumps(params), verify=verify_ssl)

if response.status_code != 200:
    print(f"Error: Failed to fetch edges (HTTP {response.status_code})", file=sys.stderr)
    sys.exit(1)

edges = response.json()
print(f"Found {len(edges)} edges\n")

# Step 3: Pre-check — show current PKI mode for each edge
needs_update = []
already_set = []

print(f"{'Edge Name':<40} {'Edge ID':<10} {'Current PKI Mode':<30} {'Action'}")
print("-" * 100)

for edge in edges:
    edge_id = edge.get("id")
    edge_name = edge.get("name", "Unknown")
    current_mode = edge.get("endpointPkiMode", "NOT_SET")

    if current_mode == TARGET_PKI_MODE:
        already_set.append(edge)
        action = "No change needed"
    else:
        needs_update.append(edge)
        action = f"Will update to {TARGET_PKI_MODE}"

    print(f"{edge_name:<40} {edge_id:<10} {current_mode:<30} {action}")

# Step 4: Summary
print(f"\n{'=' * 60}")
print(f"Summary:")
print(f"  Total edges:          {len(edges)}")
print(f"  Already set:          {len(already_set)}")
print(f"  Need update:          {len(needs_update)}")
print(f"  Target PKI mode:      {TARGET_PKI_MODE}")
print(f"{'=' * 60}")

if not needs_update:
    print("\nAll edges already have certificate-based authentication enabled.")
    sys.exit(0)

if dry_run:
    print("\n[DRY RUN] No changes made. Remove --dry-run to execute.")
    sys.exit(0)

# Step 5: Confirm
if not auto_yes:
    confirm = input(f"\nUpdate {len(needs_update)} edges to {TARGET_PKI_MODE}? (y/N): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

# Step 6: Update each edge
print(f"\nUpdating {len(needs_update)} edges...")
results = {"success": [], "failed": []}

for i, edge in enumerate(needs_update, 1):
    edge_id = edge.get("id")
    edge_name = edge.get("name", "Unknown")

    params = {
        "id": edge_id,
        "enterpriseId": enterprise_id,
        "_update": {
            "endpointPkiMode": TARGET_PKI_MODE
        }
    }

    response = requests.post(update_edge_attributes, headers=headers, data=json.dumps(params), verify=verify_ssl)

    if response.status_code == 200:
        resp_data = response.json()
        if isinstance(resp_data, dict) and resp_data.get("error"):
            print(f"  [{i}/{len(needs_update)}] {edge_name} (ID: {edge_id}) - FAILED: {resp_data['error']}")
            results["failed"].append({"id": edge_id, "name": edge_name, "error": resp_data["error"]})
        else:
            print(f"  [{i}/{len(needs_update)}] {edge_name} (ID: {edge_id}) - Updated")
            results["success"].append({"id": edge_id, "name": edge_name})
    else:
        print(f"  [{i}/{len(needs_update)}] {edge_name} (ID: {edge_id}) - FAILED (HTTP {response.status_code})")
        results["failed"].append({"id": edge_id, "name": edge_name, "error": f"HTTP {response.status_code}"})

# Step 7: Verify
print(f"\nVerifying changes...")
params = {
    "enterpriseId": enterprise_id,
    "with": ["certificates"]
}
response = requests.post(get_enterprise_edges, headers=headers, data=json.dumps(params), verify=verify_ssl)

verified = 0
if response.status_code == 200:
    updated_edges = response.json()
    for edge in updated_edges:
        if edge.get("endpointPkiMode") == TARGET_PKI_MODE:
            verified += 1

# Step 8: Write results
output = {
    "enterprise": {"id": enterprise_id, "name": enterprise_name},
    "targetPkiMode": TARGET_PKI_MODE,
    "totalEdges": len(edges),
    "updated": len(results["success"]),
    "failed": len(results["failed"]),
    "alreadySet": len(already_set),
    "verified": verified,
    "results": results
}

output_file = "setCertificateAuthResults.txt"
with open(output_file, "w") as f:
    f.write(json.dumps(output, indent=2))

# Final summary
print(f"\n{'=' * 60}")
print(f"Results:")
print(f"  Updated successfully: {len(results['success'])}")
print(f"  Failed:              {len(results['failed'])}")
print(f"  Verified:            {verified}/{len(edges)} edges now using {TARGET_PKI_MODE}")
print(f"\nResults saved to {output_file}")
