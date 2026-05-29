#!/bin/sh
set -e

echo "Esperando resolución DNS de postgres y redis…"
python - <<'PY'
import socket
import sys
import time

hosts = ("postgres", "redis")
for host in hosts:
    for attempt in range(90):
        try:
            socket.gethostbyname(host)
            print(f"  ✓ {host}")
            break
        except socket.gaierror:
            time.sleep(1)
    else:
        print(f"  ✗ No se pudo resolver {host} tras 90s", file=sys.stderr)
        sys.exit(1)
PY

exec "$@"
