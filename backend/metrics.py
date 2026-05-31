from prometheus_client import Counter, Histogram

REQUEST_COUNTER = Counter(
    "api_requests_total",
    "Total de requests HTTP",
    ["method", "endpoint"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "Duración de requests HTTP en segundos",
    ["method", "endpoint", "status"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

HTTP_ERRORS = Counter(
    "http_errors_total",
    "Requests HTTP con error (4xx/5xx)",
    ["method", "endpoint", "status"],
)

HTTP_TIMEOUTS = Counter(
    "http_timeouts_total",
    "Requests HTTP que superan el umbral de timeout",
    ["method", "endpoint"],
)

SQL_QUERIES = Counter(
    "sql_queries_total",
    "Consultas SQL ejecutadas contra PostgreSQL",
    ["query"],
)

CACHE_HIT_COUNTER = Counter(
    "cache_hits_total",
    "Respuestas servidas desde caché Redis",
    ["cache_key"],
)

CACHE_MISS_COUNTER = Counter(
    "cache_misses_total",
    "Respuestas con consulta a PostgreSQL por MISS de caché",
    ["cache_key"],
)

REQUEST_TIMEOUT_SECONDS = 5.0
