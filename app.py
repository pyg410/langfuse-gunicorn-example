"""
FastAPI + Gunicorn + Langfuse v2.60.10

1. issue case command : gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --preload
2. normal case command : gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker

if server is started, do this command - $ curl loaclhost:8000/

"""

import logging
import os

from fastapi import FastAPI
from langfuse import Langfuse
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

langfuse = Langfuse()


def get_langfuse() -> Langfuse:
    return langfuse


app = FastAPI()


@app.get("/")
async def root():
    lf = get_langfuse()
    pid = os.getpid()

    trace = lf.trace(
        name="root-request",
        metadata={"pid": pid},
    )
    generation = trace.generation(
        name="dummy-llm-call",
        model="gpt-4o",
        input={"prompt": "Hello!"},
        output={"response": "Hi there!"},
        usage={"input": 10, "output": 5, "total": 15, "unit": "TOKENS"},
    )
    generation.end()

    logger.debug(f"[PID {pid}] trace_id={trace.id} created")

    return {
        "pid": pid,
        "trace_id": trace.id,
        "message": "trace creating completed",
    }

