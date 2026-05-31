#!/usr/bin/env python3
"""
Benchmark estilo Apache Bench (ab) contra la API de ShopNow.

Uso:
  pip install httpx
  python scripts/simulate_requests.py -n 1000 -c 100 http://localhost:8000/productos/15

Equivalente a:
  ab -n 1000 -c 100 http://localhost:8000/productos/15
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import sys
import time
from dataclasses import dataclass, field

try:
    import httpx
except ImportError:
    print("Falta httpx. Instálalo con: pip install httpx", file=sys.stderr)
    sys.exit(1)

DEFAULT_URL = "http://localhost:8000/productos/15"


@dataclass
class RequestResult:
    status: int | None
    latency_ms: float
    cache: str
    error: str | None = None


@dataclass
class BenchmarkSummary:
    url: str
    requests: int
    concurrency: int
    results: list[RequestResult] = field(default_factory=list)
    wall_time_s: float = 0.0

    @property
    def ok(self) -> int:
        return sum(1 for r in self.results if r.error is None and r.status is not None and r.status < 400)

    @property
    def failed(self) -> int:
        return self.requests - self.ok

    @property
    def cache_hits(self) -> int:
        return sum(1 for r in self.results if r.cache == "HIT")

    @property
    def cache_misses(self) -> int:
        return sum(1 for r in self.results if r.cache == "MISS")

    @property
    def latencies_ms(self) -> list[float]:
        return [r.latency_ms for r in self.results if r.error is None]


async def _send_request(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
) -> RequestResult:
    async with semaphore:
        started = time.perf_counter()
        try:
            response = await client.get(url)
            latency_ms = (time.perf_counter() - started) * 1000
            return RequestResult(
                status=response.status_code,
                latency_ms=latency_ms,
                cache=response.headers.get("X-Cache", "-"),
            )
        except httpx.HTTPError as exc:
            latency_ms = (time.perf_counter() - started) * 1000
            return RequestResult(
                status=None,
                latency_ms=latency_ms,
                cache="-",
                error=str(exc),
            )


async def run_ab_test(
    requests: int,
    concurrency: int,
    url: str,
    *,
    verbose: bool = False,
    progress_every: int = 100,
) -> BenchmarkSummary:
    if requests < 1:
        raise ValueError("-n debe ser >= 1")
    if concurrency < 1:
        raise ValueError("-c debe ser >= 1")

    semaphore = asyncio.Semaphore(concurrency)
    summary = BenchmarkSummary(url=url, requests=requests, concurrency=concurrency)

    print("=== Benchmark estilo ab ===")
    print(f"Comando equivalente:")
    print(f"  ab -n {requests} -c {concurrency} {url}")
    print()

    wall_start = time.perf_counter()
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [_send_request(client, semaphore, url) for _ in range(requests)]
        completed = 0
        for coro in asyncio.as_completed(tasks):
            result = await coro
            summary.results.append(result)
            completed += 1

            if verbose:
                mark = "OK" if result.error is None and result.status and result.status < 400 else "ERR"
                status = result.status if result.status is not None else "---"
                print(
                    f"[{completed:04d}/{requests}] {mark} {status} "
                    f"{result.latency_ms:7.1f} ms  X-Cache={result.cache}"
                )
            elif completed % progress_every == 0 or completed == requests:
                print(f"  progreso: {completed}/{requests} requests completados…")

    summary.wall_time_s = time.perf_counter() - wall_start
    print_summary(summary)
    return summary


def print_summary(summary: BenchmarkSummary) -> None:
    latencies = summary.latencies_ms

    print()
    print("=== Resultados ===")
    print(f"URL:                  {summary.url}")
    print(f"Requests:             {summary.requests}")
    print(f"Concurrencia:         {summary.concurrency}")
    print(f"Tiempo total:         {summary.wall_time_s:.3f} s")
    print(f"Exitosas:             {summary.ok}")
    print(f"Fallidas:             {summary.failed}")
    print(f"Caché HIT:            {summary.cache_hits}")
    print(f"Caché MISS:           {summary.cache_misses}")

    if summary.wall_time_s > 0:
        rps = summary.requests / summary.wall_time_s
        print(f"Requests por segundo: {rps:.2f} [#/sec]")
        if latencies:
            print(f"Tiempo por request:   {statistics.mean(latencies):.2f} ms (promedio)")

    if latencies:
        print(f"Latencia mín:         {min(latencies):.1f} ms")
        print(f"Latencia máx:         {max(latencies):.1f} ms")
        if len(latencies) > 1:
            p95_index = max(0, int(len(latencies) * 0.95) - 1)
            print(f"Latencia p95:         {sorted(latencies)[p95_index]:.1f} ms")

    print()
    print("Revisa los gráficos en Grafana: http://localhost:3000")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark estilo ab para ShopNow API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python scripts/simulate_requests.py -n 1000 -c 100 http://localhost:8000/productos/15\n"
            "  python scripts/simulate_requests.py -n 100 -c 10 http://localhost:8000/api/products?popular=true"
        ),
    )
    parser.add_argument("-n", type=int, default=10, help="Número total de requests (default: 10)")
    parser.add_argument("-c", type=int, default=1, help="Nivel de concurrencia (default: 1)")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help=f"URL completa (default: {DEFAULT_URL})")
    parser.add_argument("--verbose", action="store_true", help="Imprime cada request")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    progress_every = max(1, min(100, args.n // 10 or 1))
    verbose = args.verbose or args.n <= 20

    try:
        asyncio.run(
            run_ab_test(
                args.n,
                args.c,
                args.url,
                verbose=verbose,
                progress_every=progress_every,
            )
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
