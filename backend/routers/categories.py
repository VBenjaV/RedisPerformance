from fastapi import APIRouter, Response

from cache import CACHE_KEYS, get_or_load
import repositories

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("")
def list_categories(response: Response):
    data, cache_status = get_or_load(
        CACHE_KEYS["categories"],
        repositories.fetch_categories,
    )
    response.headers["X-Cache"] = cache_status
    return data
