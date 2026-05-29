"""
Subscriber de analytics — TODO ESTUDIANTE

Agregar métricas: contadores en Redis, Prometheus custom, etc.
"""

from pubsub import push_event_log
from redis_client import get_redis
from subscribers._base import run_subscriber


def handle_order(event: dict):
    order_id = event.get("order_id")
    total = event.get("total", 0)

    # TODO ESTUDIANTE: incrementar métricas de negocio (ventas del día, top productos)
    r = get_redis()
    r.incr("analytics:orders:total")
    r.incrbyfloat("analytics:revenue:total", float(total))

    push_event_log(
        f"Analytics registró orden #{order_id} (${total:.2f})",
        "analytics-subscriber",
    )
    print(f"[analytics] orden {order_id} → revenue +{total}", flush=True)


if __name__ == "__main__":
    run_subscriber("analytics", handle_order)
