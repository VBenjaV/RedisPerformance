from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import Counter, generate_latest

from db.connection import wait_for_db
from redis_client import wait_for_redis
from routers import categories, offers, orders, products, system

REQUEST_COUNTER = Counter(
    "api_requests_total",
    "Total de requests HTTP",
    ["method", "endpoint"],
)
CACHE_HIT_COUNTER = Counter("cache_hits_total", "Respuestas servidas desde caché Redis")
CACHE_MISS_COUNTER = Counter("cache_misses_total", "Respuestas con consulta a PostgreSQL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_db()
    wait_for_redis()
    yield


app = FastAPI(
    title="ShopNow API",
    description="Backend distribuido — taller evaluado Semana 11",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(offers.router)
app.include_router(orders.router)
app.include_router(system.router)


@app.get("/")
def root():
    return {
        "message": "ShopNow Distributed API",
        "docs": "/docs",
        "guide": "Ver GUIA_ALUMNO.md en la raíz del repositorio",
    }


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain; version=0.0.4")
