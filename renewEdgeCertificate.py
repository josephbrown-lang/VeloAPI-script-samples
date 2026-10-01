"""
renewEdgeCertificate.py - Renew the PKI certificate for a VeloCloud edge.

Calls the pki/renewEdgeCertificate API (v1) to trigger certificate renewal.
The renewal is asynchronous -- the edge picks up the new certificate on its
next heartbeat.

Uses VCO_EDGE_ID and VCO_ENTERPRISE_ID from .env by default.

Usage:
  python renewEdgeCertificate.py
  python renewEdgeCertificate.py --edge-id 123
  python renewEdgeCertificate.py --edge-id 123 --enterprise-id 456
"""

import json
import sys
import argparse
import requests
from config import get_config


def parse_args():
    parser = argparse.ArgumentParser(description="Renew edge PKI certificate")
    parser.add_argument("--edge-id", type=int,
                        help="Edge ID (default: VCO_EDGE_ID from .env)")
    parser.add_argument("--enterprise-id", type=int,
                        help="Enterprise ID (default: VCO_ENTERPRISE_ID from .env)")
    return parser.parse_args()


def main():
    args = parse_args()
    config = get_config(enterprise_id=args.enterprise_id, edge_id=args.edge_id)

    headers = config['headers']
    vco_url = config['vco_url_v1']
    verify_ssl = config['verify_ssl']
    enterprise_id = config.get('enterprise_id')
    edge_id = config.get('edge_id')

    if not edge_id:
        print("Error: edge_id is required. Set VCO_EDGE_ID in .env or use --edge-id",
              file=sys.stderr)
        sys.exit(1)

    params = {"edgeId": edge_id}

    print(f"VCO: {config['vco_hostname']}")
    if enterprise_id:
        print(f"Enterprise ID: {enterprise_id}")
    print(f"Renewing certificate for edge ID: {edge_id}")

    response = requests.post(
        vco_url + 'pki/renewEdgeCertificate',
        headers=headers,
        data=json.dumps(params),
        verify=verify_ssl,
    )

    if response.status_code == 200:
        resp_data = response.json()
        print(f"\nSuccess: Certificate renewal initiated")
        with open("renewEdgeCertificate_output.txt", "w") as f:
            f.write(json.dumps(resp_data, indent=2))
        print(f"Response saved to: renewEdgeCertificate_output.txt")
        print(f"\nThe edge will pick up the new certificate on its next heartbeat.")
    else:
        print(f"\nFailed: HTTP {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    main()
