"""
Subscriber de correos — TODO ESTUDIANTE

Simula envío de email de confirmación.
En producción integrarían SMTP, SendGrid, etc.
"""

from pubsub import push_event_log
from subscribers._base import run_subscriber


def handle_order(event: dict):
    order_id = event.get("order_id")
    email = event.get("customer_email")

    # TODO ESTUDIANTE: plantilla de email, reintentos, dead-letter queue
    push_event_log(
        f"Email de confirmación enviado a {email} (orden #{order_id})",
        "email-subscriber",
    )
    print(f"[email] confirmación → {email}", flush=True)


if __name__ == "__main__":
    run_subscriber("email", handle_order)
