import time

import redis

from config import settings

_redis: redis.Redis | None = None
_redis_listener: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
    return _redis


def get_redis_listener() -> redis.Redis:
    """Cliente dedicado para Pub/Sub (listen bloqueante sin timeout de socket)."""
    global _redis_listener
    if _redis_listener is None:
        _redis_listener = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=None,
            retry_on_timeout=True,
            health_check_interval=30,
        )
    return _redis_listener


def wait_for_redis(retries: int = 90, delay: float = 1.0):
    for attempt in range(retries):
        try:
            get_redis().ping()
            return
        except redis.RedisError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
