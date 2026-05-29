import time

import redis

from config import settings

_redis: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def wait_for_redis(retries: int = 90, delay: float = 1.0):
    for attempt in range(retries):
        try:
            get_redis().ping()
            return
        except redis.RedisError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
