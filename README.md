# Serverless Data Pipeline

Order processing pipeline on AWS: SQS -> Lambda -> DynamoDB.

## Architecture

```
                    ┌──────────┐
SQS Queue ───────>  │  Lambda  │ ───────> DynamoDB
(BatchSize=10)      │ (parallel│
                    │  + retry)│
                    └────┬─────┘
                         │ failures after 3 attempts
                         v
                    Dead Letter Queue
                    (DLQ + CloudWatch Alarm)
```

## Deploy

```bash
sam build
sam deploy --guided
```

## Test

```bash
python tests/send_test_messages.py --queue-url <QUEUE_URL> --count 50 --burst
```

## Fixes Applied

| Problem (Baseline) | Fix |
|---|---|
| Sequential processing — timeout under load | Parallel with `ThreadPoolExecutor` |
| BatchSize=1 — one Lambda per message | BatchSize=10 — process 10 records per invocation |
| No DLQ — failed messages lost forever | DLQ with `maxReceiveCount: 3` + CloudWatch alarm |
| No concurrency controls — uncontrolled fan-out | `ReservedConcurrentExecutions: 5` |
| No retries on transient errors | Exponential backoff retry (3 attempts) |
| Entire batch fails if one record fails | `ReportBatchItemFailures` — only retry failed records |
| Timeout=30s, Memory=256MB | Timeout=60s, Memory=512MB |

## Latency

- **Before:** ~500ms per record sequentially = ~5s for 10 records
- **After:** ~500ms for 10 records in parallel (< 3s total batch processing)
