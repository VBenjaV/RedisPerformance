"""
Capa de caché Redis — Etapa 2 y 3 del taller.

Los estudiantes deben completar/mejorar:
- invalidate_product_caches()
- Estrategia de TTL e invalidación por categoría
"""

import json
import time
from typing import Any

from config import settings
from redis_client import get_redis

CACHE_KEYS = {
    "categories": "cache:categories:all",
    "products_popular": "cache:products:popular",
    "products_category": "cache:products:category:{category_id}",
    "offers": "cache:offers:active",
    "product_detail": "cache:product:{product_id}",
}


def _simulate_slow_query():
    if settings.simulated_db_latency_ms > 0:
        time.sleep(settings.simulated_db_latency_ms / 1000)


def cache_get(key: str) -> tuple[Any | None, str]:
    raw = get_redis().get(key)
    if raw is None:
        return None, "MISS"
    return json.loads(raw), "HIT"


def cache_set(key: str, value: Any):
    get_redis().setex(key, settings.cache_ttl_seconds, json.dumps(value, default=str))


def invalidate_product_caches(product_id: int | None = None, category_id: int | None = None):
    """
    TODO ESTUDIANTE (Etapa 3):
    Invalidar todas las claves afectadas cuando cambia el stock o un producto.
    Pista: usar CACHE_KEYS y delete de Redis; considerar category_id del producto.
    """
    r = get_redis()
    keys = [CACHE_KEYS["products_popular"], CACHE_KEYS["offers"]]
    if category_id is not None:
        keys.append(CACHE_KEYS["products_category"].format(category_id=category_id))
    if product_id is not None:
        keys.append(CACHE_KEYS["product_detail"].format(product_id=product_id))
    if keys:
        r.delete(*keys)
    # TODO: invalidar también cache:categories:all si aplica


def get_or_load(key: str, loader) -> tuple[Any, str]:
    cached, status = cache_get(key)
    if cached is not None:
        return cached, status
    _simulate_slow_query()
    data = loader()
    cache_set(key, data)
    return data, "MISS"
