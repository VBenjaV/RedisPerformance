from fastapi import APIRouter, Response

from cache import CACHE_KEYS, get_or_load
import repositories

router = APIRouter(prefix="/api/offers", tags=["offers"])


@router.get("")
def list_offers(response: Response):
    data, cache_status = get_or_load(CACHE_KEYS["offers"], repositories.fetch_offers)
    response.headers["X-Cache"] = cache_status
    return data
