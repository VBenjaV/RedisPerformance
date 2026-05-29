"""
Subscriber de inventario — TODO ESTUDIANTE

Responsabilidades sugeridas:
- Validar stock post-orden
- Registrar movimientos
- Disparar invalidación de caché si el stock cambia aquí
"""

from cache import invalidate_product_caches
from pubsub import push_event_log
from subscribers._base import run_subscriber


def handle_order(event: dict):
    order_id = event.get("order_id")
    items = event.get("items", [])

    # TODO ESTUDIANTE: implementar lógica de inventario (alertas, reservas, etc.)
    for item in items:
        invalidate_product_caches(product_id=item["product_id"])

    push_event_log(
        f"Inventario procesó orden #{order_id} ({len(items)} ítems)",
        "inventory-subscriber",
    )
    print(f"[inventory] orden {order_id} procesada", flush=True)


if __name__ == "__main__":
    run_subscriber("inventory", handle_order)
