import json

from fastapi import APIRouter

from config import settings
from redis_client import get_redis

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/events")
def recent_events():
    """Feed de actividad para el dashboard (subscribers escriben aquí)."""
    raw = get_redis().lrange(settings.events_list_key, 0, 19)
    return [json.loads(item) for item in raw]


@router.get("/health")
def health():
    return {"status": "ok", "service": "shopnow-api"}
