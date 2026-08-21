import argparse
import csv
import json
import math
import sys
import time
from datetime import datetime, timedelta, timezone
import requests
from config import get_config

########## VCO Configuration

config = get_config()

token = config['token']
vco_url = config['vco_url_v1']
verify_ssl = config['verify_ssl']
enterprise_id = config.get('enterprise_id')
edge_id = config.get('edge_id')

headers = config['headers']

######## VCO API Methods

get_edge_link_series = vco_url + 'metrics/getEdgeLinkSeries'

######## Configuration

DAYS = 30
SAMPLE_INTERVAL_SEC = 300  # 5 minutes
SAMPLES_PER_DAY = 288      # 24h / 5min

######## Helper Functions

def percentile_95(values):
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    index = int(math.ceil(0.95 * len(sorted_vals))) - 1
    return sorted_vals[index]


def bytes_to_mbps(byte_count, interval_sec=SAMPLE_INTERVAL_SEC):
    return (byte_count * 8) / interval_sec / 1_000_000


def fetch_day_samples(date, enterprise_id, edge_id):
    start_dt = datetime(date.year, date.month, date.day, tzinfo=timezone.utc)
    end_dt = start_dt + timedelta(days=1)
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)

    params = {
        "enterpriseId": enterprise_id,
        "edgeId": edge_id,
        "interval": {"start": start_ms, "end": end_ms},
        "metrics": ["bytesTx", "bytesRx"]
    }

    response = requests.post(get_edge_link_series, headers=headers,
                             data=json.dumps(params), verify=verify_ssl)

    if response.status_code != 200:
        return None, f"HTTP {response.status_code}"

    return response.json(), None


def process_day_samples(data):
    time_buckets = {}

    for link in data:
        series_list = link.get("series", [])

        metrics_by_name = {}
        for s in series_list:
            metrics_by_name[s.get("metric")] = s

        tx_metric = metrics_by_name.get("bytesTx")
        rx_metric = metrics_by_name.get("bytesRx")

        if not tx_metric and not rx_metric:
            continue

        start_time = (tx_metric or rx_metric).get("startTime", 0)
        tick_interval = (tx_metric or rx_metric).get("tickInterval", SAMPLE_INTERVAL_SEC * 1000)
        tx_data = tx_metric.get("data", []) if tx_metric else []
        rx_data = rx_metric.get("data", []) if rx_metric else []

        num_points = max(len(tx_data), len(rx_data))
        for i in range(num_points):
            ts = start_time + i * tick_interval
            bytes_tx = tx_data[i] if i < len(tx_data) and tx_data[i] is not None else 0
            bytes_rx = rx_data[i] if i < len(rx_data) and rx_data[i] is not None else 0

            if ts not in time_buckets:
                time_buckets[ts] = {"tx": 0, "rx": 0}
            time_buckets[ts]["tx"] += bytes_tx
            time_buckets[ts]["rx"] += bytes_rx

    interval_sec = tick_interval / 1000 if time_buckets else SAMPLE_INTERVAL_SEC

    timestamps = []
    tx_mbps_samples = []
    rx_mbps_samples = []
    combined_mbps_samples = []

    for ts in sorted(time_buckets.keys()):
        tx_mbps = bytes_to_mbps(time_buckets[ts]["tx"], interval_sec)
        rx_mbps = bytes_to_mbps(time_buckets[ts]["rx"], interval_sec)
        combined = tx_mbps + rx_mbps

        timestamps.append(ts)
        tx_mbps_samples.append(tx_mbps)
        rx_mbps_samples.append(rx_mbps)
        combined_mbps_samples.append(combined)

    return timestamps, tx_mbps_samples, rx_mbps_samples, combined_mbps_samples


######################### Main Program #####################

parser = argparse.ArgumentParser(description="Calculate 95th percentile bandwidth for a VeloCloud edge")
parser.add_argument("--samples", action="store_true",
                    help="Export all 5-minute samples to a CSV file")
args = parser.parse_args()

if not enterprise_id:
    print("Error: Enterprise ID not configured!", file=sys.stderr)
    print("Please run setup_config.py", file=sys.stderr)
    sys.exit(1)

if not edge_id:
    print("Error: Edge ID not configured!", file=sys.stderr)
    print("Please run setup_config.py and provide an Edge ID", file=sys.stderr)
    sys.exit(1)

print(f"95th Percentile Bandwidth Report")
print(f"Enterprise: {enterprise_id}  Edge: {edge_id}")
print(f"Period: {DAYS} days, 5-minute samples")
print(f"{'=' * 70}")

daily_tx_p95 = []
daily_rx_p95 = []
daily_combined_p95 = []
daily_details = []
all_samples = []

today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

for day_offset in range(1, DAYS + 1):
    date = today - timedelta(days=day_offset)
    date_str = date.strftime("%Y-%m-%d")

    data, err = fetch_day_samples(date, enterprise_id, edge_id)

    if err:
        print(f"  Day {day_offset:2d} ({date_str}): ERROR - {err}")
        daily_details.append({"date": date_str, "error": err})
        continue

    if not data:
        print(f"  Day {day_offset:2d} ({date_str}): No data")
        daily_details.append({"date": date_str, "samples": 0})
        continue

    ts_list, tx_samples, rx_samples, combined_samples = process_day_samples(data)

    if not combined_samples:
        print(f"  Day {day_offset:2d} ({date_str}): No samples")
        daily_details.append({"date": date_str, "samples": 0})
        continue

    if args.samples:
        for i, ts in enumerate(ts_list):
            all_samples.append((date_str, ts, tx_samples[i], rx_samples[i], combined_samples[i]))

    tx_p95 = percentile_95(tx_samples)
    rx_p95 = percentile_95(rx_samples)
    combined_p95 = percentile_95(combined_samples)

    daily_tx_p95.append(tx_p95)
    daily_rx_p95.append(rx_p95)
    daily_combined_p95.append(combined_p95)

    daily_details.append({
        "date": date_str,
        "samples": len(combined_samples),
        "tx_p95_mbps": round(tx_p95, 2),
        "rx_p95_mbps": round(rx_p95, 2),
        "combined_p95_mbps": round(combined_p95, 2)
    })

    print(f"  Day {day_offset:2d} ({date_str}): Tx={tx_p95:8.2f} Mbps  "
          f"Rx={rx_p95:8.2f} Mbps  Combined={combined_p95:8.2f} Mbps  "
          f"({len(combined_samples)} samples)")

    time.sleep(0.5)

# Final 95th percentile of daily 95th percentiles
print(f"\n{'=' * 70}")

if daily_combined_p95:
    final_tx = percentile_95(daily_tx_p95)
    final_rx = percentile_95(daily_rx_p95)
    final_combined = percentile_95(daily_combined_p95)

    print(f"  30-Day 95th Percentile Results:")
    print(f"    Tx:       {final_tx:8.2f} Mbps")
    print(f"    Rx:       {final_rx:8.2f} Mbps")
    print(f"    Combined: {final_combined:8.2f} Mbps  (Tx + Rx per sample)")
    print(f"    Days with data: {len(daily_combined_p95)}/{DAYS}")
else:
    final_tx = 0
    final_rx = 0
    final_combined = 0
    print("  No data available for any day in the period.")

print(f"{'=' * 70}")

# Write results
output = {
    "enterpriseId": enterprise_id,
    "edgeId": edge_id,
    "periodDays": DAYS,
    "sampleIntervalSec": SAMPLE_INTERVAL_SEC,
    "daysWithData": len(daily_combined_p95),
    "result": {
        "tx_p95_mbps": round(final_tx, 2),
        "rx_p95_mbps": round(final_rx, 2),
        "combined_p95_mbps": round(final_combined, 2)
    },
    "dailyDetails": daily_details
}

output_file = "get95thPercentileResults.txt"
with open(output_file, "w") as f:
    f.write(json.dumps(output, indent=2))

print(f"\nResults saved to {output_file}")

if args.samples and all_samples:
    samples_file = "get95thPercentileSamples.csv"
    with open(samples_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "timestamp_utc", "tx_mbps", "rx_mbps", "combined_mbps"])
        for date_str, ts_ms, tx, rx, combined in all_samples:
            ts_utc = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow([date_str, ts_utc, round(tx, 4), round(rx, 4), round(combined, 4)])
    print(f"Samples saved to {samples_file} ({len(all_samples)} rows)")
