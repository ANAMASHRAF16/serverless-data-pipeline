# Serverless Data Pipeline

Order processing pipeline on AWS: SQS -> Lambda -> DynamoDB.

## Architecture

```
SQS Queue --> Lambda (validate + enrich) --> DynamoDB
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

## Known Issues (Baseline)

- Sequential record processing — Lambda times out under load
- BatchSize=1 — one Lambda invocation per message (wasteful)
- No dead-letter queue — failed messages are lost
- No concurrency controls — uncontrolled fan-out
- No retries on transient errors
- ~500ms+ latency per record due to sequential enrichment
