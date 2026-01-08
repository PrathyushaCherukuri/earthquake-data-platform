import json
import os
import urllib.request
from datetime import datetime
import boto3
import time

s3 = boto3.client("s3")


S3_BUCKET = os.environ["S3_BUCKET"]
RAW_S3_PREFIX = os.environ["RAW_S3_PREFIX"]



USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"

def lambda_handler(event, context):

    with urllib.request.urlopen(USGS_URL, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    features = data.get("features", [])
    written = 0

    for f in features:
        quake_id = f.get("id")
        props = f.get("properties", {})

        if not quake_id or not props.get("time"):
            continue

        # 🔑 USE EVENT TIME (same logic as streaming partitioning)
        event_time = datetime.utcfromtimestamp(props["time"] / 1000)

        key = (
            f"{RAW_S3_PREFIX}"
            f"dt={event_time.date()}/"
            f"hour={event_time.hour}/"
            f"{quake_id}.json"
        )

        payload = {
            "source": "usgs_backfill",        # 🔑 same structure
            "ingested_at_epoch_ms": int(time.time() * 1000),
            "feature": f                      # 🔑 identical nesting
        }

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(payload),
            ContentType="application/json"
        )

        written += 1

    return {
        "status": "completed",
        "records_written": written
    }
