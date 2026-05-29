# ShopNow — Plataforma distribuida (taller evaluado)

Plantilla avanzada para el rediseño distribuido de **ShopNow** (Semana 11): FastAPI + PostgreSQL + Redis (caché y Pub/Sub) + React + Prometheus + Grafana.

## Documentación para alumnos

Lee primero **[GUIA_ALUMNO.md](./GUIA_ALUMNO.md)** — ahí está el mapa del proyecto, las etapas del PDF y **qué archivo editar en cada parte**.

## Stack

- **API:** FastAPI, psycopg2, Redis
- **Workers:** 3 subscribers (inventario, email, analytics)
- **Frontend:** React + Vite (tienda con catálogo, ofertas, carrito y feed Pub/Sub)
- **Datos:** PostgreSQL 15, Redis 7
- **Observabilidad:** Prometheus, Grafana

## Levantar

```bash
docker compose up --build
```

| Servicio | URL |
|----------|-----|
| Tienda | http://localhost:5173 |
| API Docs | http://localhost:8000/docs |
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |

## Scripts del taller

```bash
./scripts/benchmark.sh /api/products?popular=true
python scripts/simulate_orders.py   # requiere: pip install httpx
```

## Estructura rápida

```text
backend/cache.py          → Caché e invalidación (Etapas 2–3)
backend/subscribers/      → Pub/Sub workers (laboratorio guiado)
frontend/src/App.jsx      → UI de la tienda
GUIA_ALUMNO.md            → Guía completa para el alumno
```
