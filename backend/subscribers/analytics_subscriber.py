"""
Subscriber de analytics — Etapa 4.
Escucha order.created y registra métricas de negocio en Redis.
"""

from pubsub import EVENT_ORDER_CREATED, push_event_log
from redis_client import get_redis
from subscribers._base import run_subscriber


def handle_event(event: dict):
    if event.get("type") != EVENT_ORDER_CREATED:
        return

    order_id = event.get("order_id")
    total = float(event.get("total", 0))
    items = event.get("items", [])

    r = get_redis()
    r.incr("analytics:orders:total")
    r.incrbyfloat("analytics:revenue:total", total)
    for item in items:
        r.hincrby("analytics:products:sold", str(item["product_id"]), item["quantity"])

    push_event_log(
        f"Analytics registró orden #{order_id} (${total:.2f}, {len(items)} ítems)",
        "analytics-subscriber",
    )
    print(f"[analytics] orden {order_id} → revenue +{total}", flush=True)


if __name__ == "__main__":
    run_subscriber("analytics", handle_event)
