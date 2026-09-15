"""
createEdgesFromCSV.py - Bulk provision edges in VCO from a CSV file.

CSV columns:
  name            (required) Edge name
  modelNumber     (optional) e.g. edge500, edge510, edge610, edge620, edge640,
                             edge680, edge840, edge1000, edge3400, edge3800, virtual
                             Default: edge640
  configurationId (optional) Profile ID to bind the edge to
  serialNumber    (optional) Edge serial number
  haEnabled       (optional) true/false - enable HA
  description     (optional) Edge description
  contactName     (optional) Site contact name
  contactEmail    (optional) Site contact email
  contactPhone    (optional) Site contact phone
  streetAddress   (optional) Site street address
  city            (optional) Site city
  state           (optional) Site state/province
  postalCode      (optional) Site postal/zip code
  country         (optional) Site country
  lat             (optional) Site latitude
  lon             (optional) Site longitude

Usage:
  python createEdgesFromCSV.py edges.csv
  python createEdgesFromCSV.py edges.csv --dry-run
  python createEdgesFromCSV.py edges.csv --output results.csv
"""

import csv
import json
import sys
import argparse
import requests
from config import get_config


VALID_MODELS = [
    "edge500", "edge510", "edge510lte", "edge520", "edge520v",
    "edge610", "edge620", "edge640", "edge680",
    "edge840", "edge1000", "edge1000qat",
    "edge3400", "edge3800", "edge3810",
    "virtual",
]

SITE_FIELDS = [
    "contactName", "contactEmail", "contactPhone", "contactMobile",
    "streetAddress", "streetAddress2", "city", "state", "postalCode", "country",
    "lat", "lon",
]


def parse_args():
    parser = argparse.ArgumentParser(description="Bulk provision VCO edges from CSV")
    parser.add_argument("csv_file", help="Path to CSV file with edge definitions")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate CSV and print what would be created without calling the API")
    parser.add_argument("--output", default="createEdgesFromCSV_results.csv",
                        help="Output CSV file for results (default: createEdgesFromCSV_results.csv)")
    parser.add_argument("--enterprise-id", type=int,
                        help="Override enterprise ID from .env")
    return parser.parse_args()


def read_csv(csv_path):
    edges = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            row = {k.strip(): v.strip() for k, v in row.items() if k}
            if not row.get("name"):
                print(f"  WARNING: Row {i} has no name, skipping")
                continue
            edges.append(row)
    return edges


def build_payload(row, enterprise_id):
    payload = {"enterpriseId": enterprise_id}

    payload["name"] = row["name"]

    model = row.get("modelNumber", "edge640").lower()
    if model and model not in VALID_MODELS:
        print(f"  WARNING: '{model}' is not a recognized model for edge '{row['name']}'")
    payload["modelNumber"] = model or "edge640"

    if row.get("configurationId"):
        try:
            payload["configurationId"] = int(row["configurationId"])
        except ValueError:
            print(f"  WARNING: Invalid configurationId '{row['configurationId']}' for edge '{row['name']}'")

    if row.get("serialNumber"):
        payload["serialNumber"] = row["serialNumber"]

    if row.get("haEnabled", "").lower() == "true":
        payload["haEnabled"] = True

    if row.get("description"):
        payload["description"] = row["description"]

    site = {}
    for field in SITE_FIELDS:
        val = row.get(field, "")
        if val:
            if field in ("lat", "lon"):
                try:
                    site[field] = float(val)
                except ValueError:
                    print(f"  WARNING: Invalid {field} '{val}' for edge '{row['name']}'")
            else:
                site[field] = val

    if row.get("name"):
        site.setdefault("name", row["name"])

    if site:
        payload["site"] = site

    return payload


def provision_edge(payload, config):
    url = config["vco_url_v1"] + "edge/edgeProvision"
    response = requests.post(
        url,
        headers=config["headers"],
        data=json.dumps(payload),
        verify=config["verify_ssl"],
    )
    return response


def main():
    args = parse_args()
    config = get_config(enterprise_id=args.enterprise_id)

    if "enterprise_id" not in config:
        print("Error: enterprise_id is required. Set VCO_ENTERPRISE_ID in .env or use --enterprise-id",
              file=sys.stderr)
        sys.exit(1)

    enterprise_id = config["enterprise_id"]

    print(f"Reading CSV: {args.csv_file}")
    edges = read_csv(args.csv_file)

    if not edges:
        print("No valid edges found in CSV.")
        sys.exit(1)

    print(f"Found {len(edges)} edge(s) to provision")
    print(f"VCO: {config['vco_hostname']}")
    print(f"Enterprise ID: {enterprise_id}")
    print()

    results = []

    for i, row in enumerate(edges, start=1):
        payload = build_payload(row, enterprise_id)
        edge_name = payload["name"]

        if args.dry_run:
            print(f"  [{i}/{len(edges)}] DRY RUN: {edge_name} (model={payload['modelNumber']})")
            results.append({
                "name": edge_name,
                "status": "dry-run",
                "edgeId": "",
                "activationKey": "",
                "error": "",
            })
            continue

        print(f"  [{i}/{len(edges)}] Provisioning: {edge_name} ... ", end="", flush=True)

        try:
            resp = provision_edge(payload, config)
            if resp.status_code == 200:
                data = resp.json()
                edge_id = data.get("id", "")
                activation_key = data.get("activationKey", "")
                print(f"OK (id={edge_id}, key={activation_key})")
                results.append({
                    "name": edge_name,
                    "status": "created",
                    "edgeId": edge_id,
                    "activationKey": activation_key,
                    "error": "",
                })
            else:
                error_msg = resp.text[:200]
                print(f"FAILED (HTTP {resp.status_code})")
                results.append({
                    "name": edge_name,
                    "status": "failed",
                    "edgeId": "",
                    "activationKey": "",
                    "error": error_msg,
                })
        except Exception as e:
            print(f"ERROR ({e})")
            results.append({
                "name": edge_name,
                "status": "error",
                "edgeId": "",
                "activationKey": "",
                "error": str(e),
            })

    output_path = args.output
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "status", "edgeId", "activationKey", "error"])
        writer.writeheader()
        writer.writerows(results)

    created = sum(1 for r in results if r["status"] == "created")
    failed = sum(1 for r in results if r["status"] in ("failed", "error"))
    dry_run = sum(1 for r in results if r["status"] == "dry-run")

    print()
    if dry_run:
        print(f"Dry run complete: {dry_run} edge(s) would be created")
    else:
        print(f"Done: {created} created, {failed} failed")
    print(f"Results written to: {output_path}")


if __name__ == "__main__":
    main()
