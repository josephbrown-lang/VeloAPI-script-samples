import json
import sys
import time
import requests
from config import get_config

########## VCO info and credentials

config = get_config()

token = config['token']
enterpriseId = config['enterprise_id']
vco_url = config['vco_url_v1']
verify_ssl = config['verify_ssl']
edgeId = config.get('edge_id')

headers = {"Content-Type": "application/json", "Authorization": token}

######## VCO API methods
get_edgeNetworkInterfaceMetrics = vco_url + 'metrics/getEdgeNetworkInterfaceMetrics'

######################### Main Program #####################

if not edgeId:
    print("Error: Edge ID not configured!", file=sys.stderr)
    print("Please run setup_config.py and provide an Edge ID, or set VCO_EDGE_ID in .env", file=sys.stderr)
    sys.exit(1)

# Compute the last hour in milliseconds since epoch
interval_end = int(time.time() * 1000)
interval_start = interval_end - (60 * 60 * 1000)

params = {
    "edgeId": edgeId,
    "enterpriseId": enterpriseId,
    "interval": {
        "start": interval_start,
        "end": interval_end
    }
}

response = requests.post(get_edgeNetworkInterfaceMetrics, headers=headers, data=json.dumps(params), verify=verify_ssl)

resp_dict = response.json()

with open("getEdgeNetworkInterfaceMetrics.txt", "w") as f:
    f.write(json.dumps(resp_dict, indent=2))

print(f"Response saved to getEdgeNetworkInterfaceMetrics.txt")
print(f"  Edge ID: {edgeId}")
print(f"  Enterprise ID: {enterpriseId}")
print(f"  Interval: {interval_start} to {interval_end}")
