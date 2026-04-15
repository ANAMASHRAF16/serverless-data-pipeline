"""
Order processing Lambda — BASELINE version.

Receives order records from SQS, validates, enriches, and stores in DynamoDB.

Problems in this version:
- Processes records one-by-one (sequential)
- No error handling for partial batch failures
- No retries on transient DynamoDB errors
- Entire batch fails if one record fails
"""

import json
import os
import time
import hashlib
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["RESULTS_TABLE"])


def process_record(record_body):
    """Validate, enrich, and store a single order."""
    order = json.loads(record_body)

    # --- validation ---
    required = ["order_id", "customer_id", "items", "total"]
    for field in required:
        if field not in order:
            raise ValueError(f"Missing required field: {field}")

    # --- enrichment (simulate slow I/O like a DB lookup or API call) ---
    time.sleep(0.5)

    enriched = {
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "items": json.dumps(order["items"]),
        "total": str(order["total"]),
        "item_count": len(order["items"]),
        "order_hash": hashlib.md5(json.dumps(order, sort_keys=True).encode()).hexdigest(),
        "status": "processed",
        "processed_at": int(time.time()),
    }

    # --- store ---
    table.put_item(Item=enriched)
    return enriched["order_id"]


def lambda_handler(event, context):
    """Process SQS records sequentially. No partial-failure handling."""
    results = []
    for record in event["Records"]:
        order_id = process_record(record["body"])
        results.append(order_id)

    return {"processed": len(results), "order_ids": results}
