"""
Subscriber de correos — Etapa 4.
Escucha payment.approved y simula envío de confirmación.
"""

from pubsub import EVENT_PAYMENT_APPROVED, push_event_log
from subscribers._base import run_subscriber


def handle_event(event: dict):
    if event.get("type") != EVENT_PAYMENT_APPROVED:
        return

    order_id = event.get("order_id")
    email = event.get("customer_email")
    total = event.get("total", 0)

    push_event_log(
        f"Email de confirmación enviado a {email} (orden #{order_id}, ${total:.2f})",
        "email-subscriber",
    )
    print(f"[email] confirmación → {email} (orden #{order_id})", flush=True)


if __name__ == "__main__":
    run_subscriber("email", handle_event)
