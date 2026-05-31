from fastapi import APIRouter, HTTPException, Query, Response

from cache import CACHE_KEYS, get_or_load, invalidate_product_caches
import repositories

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("")
def list_products(
    response: Response,
    category_id: int | None = None,
    popular: bool = False,
):
    if popular:
        key = CACHE_KEYS["products_popular"]
        loader = lambda: repositories.fetch_products(popular_only=True)
    elif category_id:
        key = CACHE_KEYS["products_category"].format(category_id=category_id)
        loader = lambda: repositories.fetch_products(category_id=category_id)
    else:
        key = CACHE_KEYS["products_all"]
        loader = lambda: repositories.fetch_products()

    data, cache_status = get_or_load(key, loader)
    response.headers["X-Cache"] = cache_status
    return data


@router.get("/{product_id}")
def get_product(product_id: int, response: Response):
    key = CACHE_KEYS["product_detail"].format(product_id=product_id)

    def loader():
        product = repositories.fetch_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return product

    try:
        data, cache_status = get_or_load(key, loader)
    except HTTPException:
        raise
    response.headers["X-Cache"] = cache_status
    return data


@router.patch("/{product_id}/stock")
def update_stock(product_id: int, stock: int = Query(..., ge=0), response: Response = None):
    """Etapa 3 — invalidación al cambiar stock."""
    updated = repositories.update_product_stock(product_id, stock)
    if not updated:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    invalidate_product_caches(product_id=product_id, category_id=updated["category_id"])
    if response:
        response.headers["X-Cache-Invalidated"] = "true"
    return updated


@router.patch("/{product_id}/price")
def update_price(product_id: int, price: float = Query(..., gt=0), response: Response = None):
    """Etapa 3 — invalidación al cambiar precio."""
    updated = repositories.update_product_price(product_id, price)
    if not updated:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    invalidate_product_caches(product_id=product_id, category_id=updated["category_id"])
    if response:
        response.headers["X-Cache-Invalidated"] = "true"
    return updated
