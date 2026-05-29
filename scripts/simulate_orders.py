#!/usr/bin/env python3
"""
Etapa 5 — Simulación concurrente de órdenes.

Uso:
  pip install httpx
  python scripts/simulate_orders.py

Con Docker:
  docker compose exec api python /app/../scripts/simulate_orders.py
  (o desde el host apuntando a localhost:8000)
"""

import asyncio
import random

import httpx

API = "http://localhost:8000"
PRODUCT_IDS = [1, 2, 3, 4, 5, 6, 7]
CONCURRENT = 10
ORDERS = 20


async def place_order(client: httpx.AsyncClient, n: int):
    items = [
        {
            "product_id": random.choice(PRODUCT_IDS),
            "quantity": random.randint(1, 2),
        }
    ]
    email = f"alumno{n}@shopnow.test"
    r = await client.post(
        f"{API}/api/orders",
        json={"customer_email": email, "items": items},
        timeout=30.0,
    )
    return r.status_code, r.json() if r.is_success else r.text


async def main():
    async with httpx.AsyncClient() as client:
        tasks = [place_order(client, i) for i in range(ORDERS)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    ok = sum(1 for r in results if isinstance(r, tuple) and r[0] == 200)
    print(f"Órdenes exitosas: {ok}/{ORDERS} (concurrencia ~{CONCURRENT})")
    print("Revisa el panel 'Actividad Pub/Sub' en http://localhost:5173")


if __name__ == "__main__":
    asyncio.run(main())
