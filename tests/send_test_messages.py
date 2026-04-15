"""
Send test orders to the SQS queue.

Usage:
    python tests/send_test_messages.py --queue-url <URL> --count 5
    python tests/send_test_messages.py --queue-url <URL> --count 100 --burst
"""

import argparse
import json
import uuid
import time
import random
import boto3

PRODUCTS = ["Widget A", "Gadget B", "Gizmo C", "Doohickey D", "Thingamajig E"]


def make_order():
    num_items = random.randint(1, 5)
    items = random.sample(PRODUCTS, num_items)
    return {
        "order_id": str(uuid.uuid4()),
        "customer_id": f"CUST-{random.randint(1000, 9999)}",
        "items": items,
        "total": round(random.uniform(10, 500), 2),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-url", required=True)
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--burst", action="store_true", help="Send all at once")
    args = parser.parse_args()

    sqs = boto3.client("sqs")

    for i in range(args.count):
        order = make_order()
        sqs.send_message(QueueUrl=args.queue_url, MessageBody=json.dumps(order))
        if not args.burst:
            time.sleep(0.1)
        if (i + 1) % 10 == 0:
            print(f"Sent {i + 1}/{args.count}")

    print(f"Done. Sent {args.count} messages.")


if __name__ == "__main__":
    main()
