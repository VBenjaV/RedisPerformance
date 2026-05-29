#!/usr/bin/env bash
# Etapa 1 — Benchmark comparativo (antes vs después de Redis)
# Uso: ./scripts/benchmark.sh [endpoint]
# Requiere: ab (Apache Bench) instalado

set -euo pipefail

BASE="${BASE_URL:-http://localhost:8000}"
ENDPOINT="${1:-/api/products?popular=true}"
REQUESTS="${REQUESTS:-200}"
CONCURRENCY="${CONCURRENCY:-20}"

echo "=== ShopNow Benchmark ==="
echo "URL: ${BASE}${ENDPOINT}"
echo "Requests: ${REQUESTS} | Concurrency: ${CONCURRENCY}"
echo ""
echo "1ª ejecución (probable MISS — vacía caché o expirada):"
ab -n "$REQUESTS" -c "$CONCURRENCY" "${BASE}${ENDPOINT}" | grep -E "Requests per second|Time per request|Failed requests"

echo ""
echo "2ª ejecución (debería ser más rápida con HIT en Redis):"
ab -n "$REQUESTS" -c "$CONCURRENCY" "${BASE}${ENDPOINT}" | grep -E "Requests per second|Time per request|Failed requests"

echo ""
echo "Verifica cabecera X-Cache con:"
echo "  curl -sI \"${BASE}${ENDPOINT}\" | grep -i x-cache"
