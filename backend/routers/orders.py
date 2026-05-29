from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from pubsub import publish_order_event, push_event_log
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
    Publisher de órdenes (Etapa Pub/Sub).
    TODO ESTUDIANTE: enriquecer el evento y mover lógica pesada a subscribers si lo desean.
    """
    try:
        order = repositories.create_order(
            body.customer_email,
            [item.model_dump() for item in body.items],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    event = {
        "type": "order.created",
        "order_id": order["order_id"],
        "customer_email": order["customer_email"],
        "total": order["total"],
        "items": [
            {"product_id": i["id"], "quantity": i["quantity"], "name": i["name"]}
            for i in order["items"]
        ],
    }
    publish_order_event(event)
    push_event_log(f"Orden #{order['order_id']} publicada en Pub/Sub", "api-publisher")
    return order
