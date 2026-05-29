import json
import sys
import time

from config import settings
from db.connection import wait_for_db
from pubsub import push_event_log
from redis_client import get_redis, wait_for_redis


def run_subscriber(name: str, handler):
    print(f"[{name}] iniciando subscriber…", flush=True)
    wait_for_db()
    wait_for_redis()
    r = get_redis()
    pubsub = r.pubsub()
    pubsub.subscribe(settings.orders_channel)
    print(f"[{name}] escuchando canal {settings.orders_channel}", flush=True)

    for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            event = json.loads(message["data"])
            handler(event)
        except Exception as exc:
            print(f"[{name}] error: {exc}", file=sys.stderr, flush=True)
            time.sleep(0.5)
