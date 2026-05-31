"""
Capa de caché Redis — Etapas 2 y 3 del taller (Cache Aside + invalidación).
"""

import json
import time
from typing import Any

from config import settings
from metrics import CACHE_HIT_COUNTER, CACHE_MISS_COUNTER
from redis_client import get_redis

CACHE_KEYS = {
    "categories": "cache:categories:all",
    "products_popular": "cache:products:popular",
    "products_all": "cache:products:all",
    "products_category": "cache:products:category:{category_id}",
    "offers": "cache:offers:active",
    "product_detail": "cache:product:{product_id}",
}


def _simulate_slow_query():
    if settings.simulated_db_latency_ms > 0:
        time.sleep(settings.simulated_db_latency_ms / 1000)


def cache_get(key: str) -> tuple[Any | None, str]:
    if not settings.cache_enabled:
        return None, "BYPASS"

    raw = get_redis().get(key)
    if raw is None:
        CACHE_MISS_COUNTER.labels(cache_key=key).inc()
        return None, "MISS"
    CACHE_HIT_COUNTER.labels(cache_key=key).inc()
    return json.loads(raw), "HIT"


def cache_set(key: str, value: Any):
    if not settings.cache_enabled:
        return
    get_redis().setex(key, settings.cache_ttl_seconds, json.dumps(value, default=str))


def invalidate_product_caches(product_id: int | None = None, category_id: int | None = None):
    """
    Etapa 3 — invalidación explícita al cambiar stock, precio o inventario post-orden.
    """
    r = get_redis()
    keys = [
        CACHE_KEYS["categories"],
        CACHE_KEYS["products_popular"],
        CACHE_KEYS["products_all"],
        CACHE_KEYS["offers"],
    ]
    if category_id is not None:
        keys.append(CACHE_KEYS["products_category"].format(category_id=category_id))
    if product_id is not None:
        keys.append(CACHE_KEYS["product_detail"].format(product_id=product_id))
    if keys:
        r.delete(*keys)


def get_or_load(key: str, loader) -> tuple[Any, str]:
    if not settings.cache_enabled:
        _simulate_slow_query()
        return loader(), "BYPASS"

    cached, status = cache_get(key)
    if cached is not None:
        return cached, status
    _simulate_slow_query()
    data = loader()
    cache_set(key, data)
    return data, "MISS"
