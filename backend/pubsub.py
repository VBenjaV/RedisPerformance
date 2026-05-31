"""
Pub/Sub de órdenes — Etapa 4 del taller.

Eventos publicados por la API y subscribers:
  • order.created      — orden registrada (inventario + analytics)
  • payment.approved   — pago simulado aprobado (correos)
  • stock.updated      — stock descontado por inventario
"""

import json
from datetime import datetime, timezone

from config import settings
from redis_client import get_redis

EVENT_ORDER_CREATED = "order.created"
EVENT_PAYMENT_APPROVED = "payment.approved"
EVENT_STOCK_UPDATED = "stock.updated"


def publish_order_event(event: dict):
    payload = {
        **event,
        "published_at": datetime.now(timezone.utc).isoformat(),
    }
    get_redis().publish(settings.orders_channel, json.dumps(payload, default=str))


def push_event_log(message: str, source: str):
    entry = json.dumps(
        {
            "message": message,
            "source": source,
            "at": datetime.now(timezone.utc).isoformat(),
        }
    )
    r = get_redis()
    r.lpush(settings.events_list_key, entry)
    r.ltrim(settings.events_list_key, 0, settings.events_list_max - 1)
