import json
import sys
import time

import redis

from config import settings
from db.connection import wait_for_db
from pubsub import push_event_log
from redis_client import get_redis_listener, wait_for_redis


def run_subscriber(name: str, handler):
    print(f"[{name}] iniciando subscriber…", flush=True)
    wait_for_db()
    wait_for_redis()
    print(f"[{name}] escuchando canal {settings.orders_channel}", flush=True)

    while True:
        pubsub = None
        try:
            listener = get_redis_listener()
            pubsub = listener.pubsub(ignore_subscribe_messages=True)
            pubsub.subscribe(settings.orders_channel)

            for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                try:
                    event = json.loads(message["data"])
                    handler(event)
                except Exception as exc:
                    print(f"[{name}] error procesando evento: {exc}", file=sys.stderr, flush=True)
                    time.sleep(0.5)
        except (redis.TimeoutError, redis.ConnectionError, redis.RedisError) as exc:
            print(f"[{name}] conexión Redis interrumpida ({exc}), reconectando en 2s…", flush=True)
            time.sleep(2)
        finally:
            if pubsub is not None:
                try:
                    pubsub.close()
                except redis.RedisError:
                    pass
