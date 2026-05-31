#!/usr/bin/env python3
"""ab -n 1000 -c 100 http://localhost:8000/productos/15"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from simulate_requests import main

if __name__ == "__main__":
    main(["-n", "1000", "-c", "100", "http://localhost:8000/productos/15"])
