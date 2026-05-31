from fastapi import APIRouter, Response

from routers.products import get_product

router = APIRouter(tags=["productos"])


@router.get("/productos/{product_id}")
def get_producto(product_id: int, response: Response):
    """Alias en español para benchmarks (ab -n 1000 -c 100 http://localhost:8000/productos/15)."""
    return get_product(product_id, response)
