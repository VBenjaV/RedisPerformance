"""
Subscriber de inventario — Etapa 4.
Escucha order.created, descuenta stock y publica stock.updated.
"""

from cache import invalidate_product_caches
from pubsub import EVENT_ORDER_CREATED, EVENT_STOCK_UPDATED, publish_order_event, push_event_log
import repositories
from subscribers._base import run_subscriber


def handle_event(event: dict):
    if event.get("type") != EVENT_ORDER_CREATED:
        return

    order_id = event.get("order_id")
    items = event.get("items", [])
    failures = 0

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]
        updated = repositories.deduct_stock(product_id, quantity)

        if updated is None:
            failures += 1
            push_event_log(
                f"Stock insuficiente: producto #{product_id} en orden #{order_id}",
                "inventory-subscriber",
            )
            print(f"[inventory] FALLA stock producto {product_id} orden {order_id}", flush=True)
            continue

        invalidate_product_caches(product_id=product_id, category_id=updated["category_id"])

        publish_order_event(
            {
                "type": EVENT_STOCK_UPDATED,
                "order_id": order_id,
                "product_id": product_id,
                "stock": updated["stock"],
                "product_name": updated["name"],
            }
        )

        if updated["stock"] <= 5:
            push_event_log(
                f"Alerta stock bajo: {updated['name']} quedó con {updated['stock']} unidades",
                "inventory-subscriber",
            )

    status = "confirmed" if failures == 0 else "inventory_partial_failure"
    repositories.update_order_status(order_id, status)

    push_event_log(
        f"Inventario procesó orden #{order_id} ({len(items) - failures}/{len(items)} ítems OK)",
        "inventory-subscriber",
    )
    print(f"[inventory] orden {order_id} → {status}", flush=True)


if __name__ == "__main__":
    run_subscriber("inventory", handle_event)
