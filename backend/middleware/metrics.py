import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from metrics import (
    HTTP_ERRORS,
    HTTP_TIMEOUTS,
    REQUEST_COUNTER,
    REQUEST_DURATION,
    REQUEST_TIMEOUT_SECONDS,
)


def _resolve_endpoint(request: Request) -> str:
    route = request.scope.get("route")
    if route is not None and hasattr(route, "path"):
        return route.path
    return request.url.path


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration = time.perf_counter() - start
            endpoint = _resolve_endpoint(request)
            REQUEST_COUNTER.labels(method=method, endpoint=endpoint).inc()
            REQUEST_DURATION.labels(method=method, endpoint=endpoint, status="500").observe(duration)
            HTTP_ERRORS.labels(method=method, endpoint=endpoint, status="500").inc()
            if duration >= REQUEST_TIMEOUT_SECONDS:
                HTTP_TIMEOUTS.labels(method=method, endpoint=endpoint).inc()
            raise

        duration = time.perf_counter() - start
        endpoint = _resolve_endpoint(request)
        status = str(response.status_code)

        REQUEST_COUNTER.labels(method=method, endpoint=endpoint).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint, status=status).observe(duration)

        if response.status_code >= 400:
            HTTP_ERRORS.labels(method=method, endpoint=endpoint, status=status).inc()

        if duration >= REQUEST_TIMEOUT_SECONDS:
            HTTP_TIMEOUTS.labels(method=method, endpoint=endpoint).inc()

        return response
