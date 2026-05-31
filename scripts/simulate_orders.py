#!/usr/bin/env python3
"""
Etapa 5 — Simulación concurrente de compras.
500 usuarios intentan comprar el mismo producto simultáneamente.

Uso:
  pip install httpx
  python scripts/simulate_orders.py
  python scripts/simulate_orders.py --product-id 15 --orders 500 --concurrency 100
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time

try:
    import httpx
except ImportError:
    print("pip install httpx", file=sys.stderr)
    sys.exit(1)

API = "http://localhost:8000"
DEFAULT_PRODUCT_ID = 15
DEFAULT_ORDERS = 500
DEFAULT_CONCURRENCY = 100


async def place_order(client: httpx.AsyncClient, n: int, product_id: int, semaphore: asyncio.Semaphore):
    async with semaphore:
        email = f"alumno{n}@gmail.com"
        payload = {"customer_email": email, "items": [{"product_id": product_id, "quantity": 1}]}
        try:
            r = await client.post(f"{API}/api/orders", json=payload, timeout=30.0)
            return r.status_code, r.json() if r.is_success else r.text
        except httpx.HTTPError as exc:
            return 0, str(exc)


async def main_async(product_id: int, orders: int, concurrency: int) -> None:
    print("=== Etapa 5 — Simulación concurrente de compras ===")
    print(f"Escenario: {orders} usuarios compran producto #{product_id} (concurrencia {concurrency})")
    print()

    semaphore = asyncio.Semaphore(concurrency)
    started = time.perf_counter()

    async with httpx.AsyncClient() as client:
        tasks = [place_order(client, i, product_id, semaphore) for i in range(orders)]
        results = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - started
    ok = sum(1 for code, _ in results if code == 200)
    failed = orders - ok

    print(f"Órdenes exitosas (API): {ok}/{orders}")
    print(f"Fallidas:             {failed}/{orders}")
    print(f"Tiempo total:         {elapsed:.2f} s")
    print(f"Throughput API:       {orders / elapsed:.1f} órdenes/s")
    print()
    print("Revisa en http://localhost:5173 el panel Pub/Sub (inventario, email, analytics).")
    print("Revisa stock final:   GET /api/products/{product_id} o /productos/{product_id}")
    print("Busca eventos de 'Stock insuficiente' si hubo sobreventa (race condition).")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Etapa 5 — 500 compras concurrentes del mismo producto")
    parser.add_argument("--product-id", type=int, default=DEFAULT_PRODUCT_ID)
    parser.add_argument("--orders", type=int, default=DEFAULT_ORDERS)
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(main_async(args.product_id, args.orders, args.concurrency))


if __name__ == "__main__":
    main()
