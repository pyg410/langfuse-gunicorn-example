# Langfuse v2 + Gunicorn `--preload` Fork-Safety Bug

## Bug

When `Langfuse()` is initialized globally with Gunicorn `--preload`, all ingestion events are silently lost in worker processes because `os.fork()` copies memory but not threads. Consumer threads only exist in the master process, so workers have no thread to drain the queue.

- Traces are never sent to Langfuse server (100% data loss)
- Calling `flush()` blocks forever → Gunicorn worker timeout → worker killed (exit code 134)

## Setup

Create a `.env` file:

```
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://jp.cloud.langfuse.com
```

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
# 1. issue case
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --preload

# 2. normal case : traces recorded correctly
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Verify

Send requests and check how many traces were recorded:

```bash
# send requests
for i in {1..10}; do curl http://localhost:8000/; done

# check recorded traces
curl -u pk-lf-...:sk-lf-... \
  "https://jp.cloud.langfuse.com/api/public/traces" | python3 -m json.tool | grep totalItems
```

| Case | Result |
|------|--------|
| `--preload` (issue) | `totalItems` does not increase |
| no `--preload` (normal) | `totalItems` increases by 10 |