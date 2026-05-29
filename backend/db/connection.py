import time

import psycopg2
from psycopg2.extras import RealDictCursor

from config import settings


def get_connection():
    return psycopg2.connect(settings.database_url, cursor_factory=RealDictCursor)


def wait_for_db(retries: int = 90, delay: float = 1.0):
    for attempt in range(retries):
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            return
        except psycopg2.OperationalError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
