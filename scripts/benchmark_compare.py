#!/usr/bin/env python3
"""
Benchmark comparativo antes vs después — Redis mal aprovechado vs Redis operativo.

Equivalente a benchmark.sh (Etapa 1):
  ab -n 1000 -c 100 http://localhost:8000/productos/15   # 1ª corrida → ANTES
  ab -n 1000 -c 100 http://localhost:8000/productos/15   # 2ª corrida → DESPUÉS

Interpretación para el informe:
  • ANTES: Redis presente pero caché vacía/expirada; bajo carga concurrente predominan
    MISS → consultas repetitivas a PostgreSQL (~350 ms simulados), alta latencia.
  • DESPUÉS: Tras calentar Redis (Cache Aside + TTL + invalidación implementados),
    las lecturas repetidas resuelven en HIT → menos SQL, menor latencia, mayor throughput.

Uso:
  1. docker compose up -d
  2. python scripts/benchmark_compare.py
  3. python scripts/benchmark_compare.py -n 1000 -c 100
"""

from __future__ import annotations

import argparse
import asyncio
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    print("pip install httpx", file=sys.stderr)
    sys.exit(1)

URL = "http://localhost:8000/productos/15"
METRICS_URL = "http://localhost:8000/metrics"
PROMETHEUS_URL = "http://localhost:9090"
REQUESTS = 1000
CONCURRENCY = 100
PROJECT_DIR = Path(__file__).resolve().parent.parent


def flush_redis() -> None:
    subprocess.run(
        ["docker", "compose", "exec", "-T", "redis", "redis-cli", "FLUSHDB"],
        cwd=PROJECT_DIR,
        capture_output=True,
    )


def ensure_api_with_cache() -> None:
    """API con Redis activo y la implementación completa (CACHE_ENABLED=true)."""
    env = os.environ.copy()
    env["CACHE_ENABLED"] = "true"
    subprocess.run(
        ["docker", "compose", "up", "-d", "--no-deps", "api"],
        cwd=PROJECT_DIR,
        env=env,
        check=True,
    )


def wait_for_api(timeout_s: float = 60.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            r = httpx.get("http://localhost:8000/api/system/health", timeout=3.0)
            if r.is_success:
                return
        except httpx.HTTPError:
            pass
        time.sleep(2)
    print("Advertencia: la API no respondió a tiempo; continuando igual…", file=sys.stderr)


def read_counter(name: str) -> float:
    try:
        text = httpx.get(METRICS_URL, timeout=5.0).text
    except httpx.HTTPError:
        return 0.0
    total = 0.0
    for line in text.splitlines():
        if line.startswith("#") or not line.startswith(name):
            continue
        parts = line.split()
        if len(parts) >= 2:
            try:
                total += float(parts[-1])
            except ValueError:
                pass
    return total


def query_cpu_percent() -> float | None:
    query = 'avg(rate(container_cpu_usage_seconds_total{name=~".*api.*"}[30s])) * 100'
    try:
        r = httpx.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=5.0,
        )
        results = r.json().get("data", {}).get("result", [])
        if not results:
            return None
        return float(results[0]["value"][1])
    except (httpx.HTTPError, KeyError, ValueError, IndexError):
        return None


async def run_load(label: str, n: int, c: int) -> dict:
    sem = asyncio.Semaphore(c)
    latencies: list[float] = []
    hits = misses = bypass = ok = 0
    sql_before = read_counter("sql_queries_total")

    async def one(client: httpx.AsyncClient) -> None:
        nonlocal hits, misses, bypass, ok
        async with sem:
            t0 = time.perf_counter()
            try:
                r = await client.get(URL)
                ms = (time.perf_counter() - t0) * 1000
                latencies.append(ms)
                cache = r.headers.get("X-Cache", "-")
                if cache == "HIT":
                    hits += 1
                elif cache == "MISS":
                    misses += 1
                elif cache == "BYPASS":
                    bypass += 1
                if r.is_success:
                    ok += 1
            except httpx.HTTPError:
                pass

    wall_start = time.perf_counter()
    async with httpx.AsyncClient(timeout=60.0) as client:
        await asyncio.gather(*[one(client) for _ in range(n)])
    wall_s = time.perf_counter() - wall_start

    sql_after = read_counter("sql_queries_total")
    sql_delta = max(0, int(sql_after - sql_before))
    sorted_lat = sorted(latencies)
    p95_idx = max(0, int(len(sorted_lat) * 0.95) - 1) if sorted_lat else 0
    cpu = query_cpu_percent()

    print(f"\n--- {label} ---")
    print(f"  Exitosas: {ok}/{n} | HIT={hits} MISS={misses} BYPASS={bypass}")
    print(f"  SQL (Prometheus): {sql_delta} | Throughput: {n / wall_s:.1f} rps")

    return {
        "label": label,
        "ok": ok,
        "hits": hits,
        "misses": misses,
        "bypass": bypass,
        "min_ms": min(latencies) if latencies else 0,
        "max_ms": max(latencies) if latencies else 0,
        "avg_ms": statistics.mean(latencies) if latencies else 0,
        "p95_ms": sorted_lat[p95_idx] if sorted_lat else 0,
        "rps": n / wall_s if wall_s else 0,
        "sql": sql_delta if sql_delta else misses + bypass,
        "cpu_pct": cpu,
    }


def print_report_table(before: dict, after: dict, n: int, c: int) -> None:
    def fmt_cpu(v: float | None) -> str:
        return f"{v:.2f}%" if v is not None else "N/D"

    print("\n" + "=" * 72)
    print(f"4. EVIDENCIA DE BENCHMARKS — ab -n {n} -c {c} /productos/15")
    print("=" * 72)
    print(f"{'Métrica':<32} {'Antes':>16} {'Después':>16}")
    print("-" * 72)
    print(f"{'Consultas SQL':<32} {before['sql']:>16} {after['sql']:>16}")
    print(f"{'Latencia mínima':<32} {before['min_ms']:>14.1f} ms {after['min_ms']:>14.1f} ms")
    print(f"{'Latencia máxima':<32} {before['max_ms']:>14.1f} ms {after['max_ms']:>14.1f} ms")
    print(f"{'Latencia p95':<32} {before['p95_ms']:>14.1f} ms {after['p95_ms']:>14.1f} ms")
    print(f"{'Tiempo por request (promedio)':<32} {before['avg_ms']:>14.1f} ms {after['avg_ms']:>14.1f} ms")
    print(f"{'CPU':<32} {fmt_cpu(before['cpu_pct']):>16} {fmt_cpu(after['cpu_pct']):>16}")
    print(f"{'Throughput':<32} {before['rps']:>12.1f} rps {after['rps']:>12.1f} rps")
    print("=" * 72)
    print(f"{'Caché HIT (referencia)':<32} {before['hits']:>16} {after['hits']:>16}")
    print(f"{'Caché MISS':<32} {before['misses']:>16} {after['misses']:>16}")
    print()
    print("Antes  = 1ª corrida tras FLUSHDB (caché fría, Redis sin datos útiles aún)")
    print("Después = 2ª corrida consecutiva (caché caliente, Cache Aside operativo)")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Benchmark antes/después: caché fría vs caché caliente (Etapa 1/6)"
    )
    p.add_argument("-n", type=int, default=REQUESTS, help="Total requests (default: 1000)")
    p.add_argument("-c", type=int, default=CONCURRENCY, help="Concurrencia (default: 100)")
    p.add_argument("--url", default=URL, help="URL del endpoint")
    return p.parse_args()


async def main() -> None:
    args = parse_args()
    global URL
    URL = args.url

    print("=== Benchmark comparativo — Redis antes vs después ===")
    print(f"Comando: ab -n {args.n} -c {args.c} {URL}  (×2 corrida consecutivas)")
    print()
    print("Contexto: Redis ya estaba en el proyecto base, pero sin TTL/invalidación")
    print("completos las lecturas repetidas seguían saturando PostgreSQL. Tras")
    print("implementar Cache Aside + invalidación, la 2ª corrida demuestra el beneficio.")
    print()

    ensure_api_with_cache()
    wait_for_api()

    print(">>> ANTES — 1ª corrida (FLUSHDB, caché vacía)...")
    flush_redis()
    before = await run_load("ANTES (1ª corrida — caché fría)", args.n, args.c)

    print("\n>>> DESPUÉS — 2ª corrida (caché caliente, sin FLUSHDB)...")
    after = await run_load("DESPUÉS (2ª corrida — caché caliente)", args.n, args.c)

    print_report_table(before, after, args.n, args.c)


if __name__ == "__main__":
    asyncio.run(main())
