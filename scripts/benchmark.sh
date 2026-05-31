#!/usr/bin/env bash
# Etapa 1 — Benchmark comparativo estilo Apache Bench
# Uso: ./scripts/benchmark.sh [url]
# Requiere: ab (Apache Bench) instalado

set -euo pipefail

URL="${1:-http://localhost:8000/productos/15}"
REQUESTS="${REQUESTS:-1000}"
CONCURRENCY="${CONCURRENCY:-100}"

echo "=== ShopNow Benchmark (ab) ==="
echo "Comando: ab -n ${REQUESTS} -c ${CONCURRENCY} ${URL}"
echo ""
echo "1ª ejecución (probable MISS — caché vacía o expirada):"
ab -n "$REQUESTS" -c "$CONCURRENCY" "$URL" | grep -E "Requests per second|Time per request|Failed requests|Non-2xx"

echo ""
echo "2ª ejecución (debería ser más rápida con HIT en Redis):"
ab -n "$REQUESTS" -c "$CONCURRENCY" "$URL" | grep -E "Requests per second|Time per request|Failed requests|Non-2xx"

echo ""
echo "Verifica cabecera X-Cache con:"
echo "  curl -sI \"${URL}\" | grep -i x-cache"
echo ""
echo "Alternativa sin ab (Python):"
echo "  python scripts/simulate_requests.py -n ${REQUESTS} -c ${CONCURRENCY} ${URL}"
echo "  python scripts/benchmark_compare.py -n ${REQUESTS} -c ${CONCURRENCY}  # antes/después"
