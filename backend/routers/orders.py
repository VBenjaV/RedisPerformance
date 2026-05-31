import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from config import settings
from pubsub import (
    EVENT_ORDER_CREATED,
    EVENT_PAYMENT_APPROVED,
    publish_order_event,
    push_event_log,
)
import repositories

router = APIRouter(prefix="/api/orders", tags=["orders"])


class OrderItemInput(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=20)


class CreateOrderInput(BaseModel):
    customer_email: EmailStr
    items: list[OrderItemInput] = Field(min_length=1)


@router.post("")
def create_order(body: CreateOrderInput):
    """
    Etapa 4 — Publisher principal.
    1. Crea la orden (rápido, sin correo/analytics/inventario síncrono).
    2. Publica order.created → inventario + analytics reaccionan en background.
    3. Simula solo validación de pago (~50 ms) y publica payment.approved → correos.
    """
    try:
        order = repositories.create_order(
            body.customer_email,
            [item.model_dump() for item in body.items],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    items_payload = [
        {"product_id": i["id"], "quantity": i["quantity"], "name": i["name"], "category_id": i["category_id"]}
        for i in order["items"]
    ]

    publish_order_event(
        {
            "type": EVENT_ORDER_CREATED,
            "order_id": order["order_id"],
            "customer_email": order["customer_email"],
            "total": order["total"],
            "items": items_payload,
        }
    )

    if settings.payment_simulation_ms > 0:
        time.sleep(settings.payment_simulation_ms / 1000)

    publish_order_event(
        {
            "type": EVENT_PAYMENT_APPROVED,
            "order_id": order["order_id"],
            "customer_email": order["customer_email"],
            "total": order["total"],
        }
    )

    push_event_log(f"Orden #{order['order_id']} publicada en Pub/Sub", "api-publisher")

    return {
        **order,
        "status": "payment_approved",
        "message": "Compra realizada correctamente. Procesos en background vía Pub/Sub.",
    }
