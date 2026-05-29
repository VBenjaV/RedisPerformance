# Guía del alumno — ShopNow Distribuido

Proyecto base para el **Mini Taller Evaluado — Rediseño Distribuido de ShopNow** (Semana 11).

El código ya funciona de punta a punta: puedes levantar la tienda, comprar productos y ver eventos en tiempo real. Tu trabajo es **mejorar** caché, invalidación, subscribers y métricas según las etapas del PDF.

---

## Objetivo del taller

| Etapa | Qué hacer | Dónde editar |
|-------|-----------|--------------|
| **1 — Diagnóstico** | Benchmark, medir latencia, detectar endpoints lentos | `scripts/benchmark.sh`, Swagger `/docs` |
| **2 — Redis caché** | Cachear productos populares, categorías y ofertas | `backend/cache.py`, routers en `backend/routers/` |
| **3 — Invalidación** | Evitar stock/categorías obsoletos en Redis | `backend/cache.py` → `invalidate_product_caches()` |
| **Pub/Sub** | Publisher + 3 subscribers desacoplados | `backend/pubsub.py`, `backend/subscribers/*.py` |
| **5 — Concurrencia** | Muchas órdenes en paralelo | `scripts/simulate_orders.py` |

Meta de referencia del PDF: latencia ~480ms → ~15ms, menos consultas SQL, mayor throughput.

---

## Cómo levantar el proyecto

```bash
docker compose up --build
```

| Servicio | URL |
|----------|-----|
| Tienda (frontend) | http://localhost:5173 |
| API + Swagger | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

**Primera compra de prueba:** agrega productos al carrito → ingresa un email → **Confirmar orden** → mira el panel **Actividad Pub/Sub** a la derecha.

---

## Estructura del repositorio

```text
shopnow-distributed-template/
├── GUIA_ALUMNO.md          ← Estás aquí
├── docker-compose.yml      ← Servicios (API, workers, DB, Redis, observabilidad)
├── scripts/
│   ├── benchmark.sh        ← Etapa 1
│   └── simulate_orders.py  ← Etapa 5
├── backend/
│   ├── main.py             ← Entrada FastAPI (no suele requerir cambios)
│   ├── config.py           ← Variables de entorno (TTL, latencia simulada)
│   ├── cache.py            ← ⭐ Caché Redis — Etapas 2 y 3
│   ├── pubsub.py           ← ⭐ Publicación de eventos de órdenes
│   ├── repositories.py     ← Consultas SQL a PostgreSQL
│   ├── db/init.sql         ← Esquema y datos de ejemplo
│   ├── routers/            ← Endpoints HTTP (uno por dominio)
│   └── subscribers/        ← ⭐ Workers: inventario, email, analytics
└── frontend/
    ├── src/App.jsx         ← Orquestación de la tienda
    ├── src/api/client.js   ← Llamadas a la API (ajusta si cambias rutas)
    └── src/components/     ← UI (puedes personalizar diseño aquí)
```

---

## Backend — por dónde empezar

### 1. Endpoints que debes entender

| Método | Ruta | Uso en el taller |
|--------|------|------------------|
| GET | `/api/categories` | Caché Etapa 2 |
| GET | `/api/products?popular=true` | Productos populares (benchmark principal) |
| GET | `/api/products?category_id=1` | Filtro por categoría |
| GET | `/api/offers` | Ofertas cacheadas |
| POST | `/api/orders` | **Publisher** de órdenes (Pub/Sub) |
| PATCH | `/api/products/{id}/stock?stock=10` | Probar **invalidación** Etapa 3 |
| GET | `/api/system/events` | Feed visible en el frontend |
| GET | `/metrics` | Prometheus |

Cada respuesta cacheada incluye la cabecera **`X-Cache: HIT`** o **`MISS`**.

### 2. `backend/cache.py` (Etapas 2 y 3)

- `get_or_load()` ya implementa patrón cache-aside.
- `SIMULATED_DB_LATENCY_MS=350` simula PostgreSQL lento en cada MISS.
- **Tu tarea:** completar `invalidate_product_caches()` para borrar todas las claves relacionadas cuando cambia el stock.

Claves definidas en `CACHE_KEYS`:

```python
cache:categories:all
cache:products:popular
cache:products:category:{id}
cache:offers:active
cache:product:{id}
```

### 3. `backend/pubsub.py` y órdenes

- Al crear una orden, `routers/orders.py` publica en el canal Redis `shopnow:orders`.
- Los tres workers escuchan el mismo canal y procesan en paralelo.

### 4. Subscribers (`backend/subscribers/`)

| Archivo | Rol | TODO del alumno |
|---------|-----|-----------------|
| `inventory_subscriber.py` | Inventario | Alertas de stock bajo, reservas |
| `email_subscriber.py` | Correos | Plantillas, reintentos |
| `analytics_subscriber.py` | Analytics | Métricas de negocio en Redis/Prometheus |

Busca comentarios `# TODO ESTUDIANTE` en el código.

### 5. Variables de entorno útiles

| Variable | Default | Descripción |
|----------|---------|-------------|
| `SIMULATED_DB_LATENCY_MS` | 350 | Retardo artificial en MISS |
| `CACHE_TTL_SECONDS` | 120 | TTL de entradas en Redis |
| `DATABASE_URL` | (compose) | PostgreSQL |
| `REDIS_URL` | (compose) | Redis |

---

## Frontend — por dónde editar

| Archivo | Para qué |
|---------|----------|
| `src/App.jsx` | Estado global: carrito, filtros, checkout, búsqueda |
| `src/api/client.js` | Rutas de la API (si agregas endpoints) |
| `src/components/ProductCard.jsx` | Tarjeta de producto |
| `src/components/CartPanel.jsx` | Carrito con cantidades +/- |
| `src/components/ActivityFeed.jsx` | Feed Pub/Sub con colores por subscriber |
| `src/components/ProductDetailModal.jsx` | Modal de detalle de producto |
| `src/styles/global.css` | Design system (colores, layout, animaciones) |
| `src/hooks/useFilteredProducts.js` | Búsqueda y orden local del catálogo |

El proxy de Vite redirige `/api/*` al contenedor `api` — no hardcodees `localhost:8000` en el navegador dentro de Docker.

**Etiquetas Redis en UI:** los badges `Redis HIT` / `Redis MISS` leen la cabecera `X-Cache` — úsalos para demostrar la mejora en la presentación.

---

## Etapa 1 — Benchmark

```bash
chmod +x scripts/benchmark.sh
./scripts/benchmark.sh /api/products?popular=true
```

Compara la 1ª y 2ª ejecución de `ab`. Documenta en tu informe:

- Requests per second
- Time per request
- Valor de `X-Cache`

También puedes usar **k6** o **Locust** (sugeridos en el PDF).

Para vaciar caché y forzar MISS:

```bash
docker compose exec redis redis-cli FLUSHDB
```

---

## Etapa 3 — Probar invalidación

1. Carga productos populares dos veces (2º HIT).
2. Actualiza stock:

```bash
curl -X PATCH "http://localhost:8000/api/products/1/stock?stock=3"
```

3. Vuelve a pedir productos — deberías ver MISS si invalidaste bien.
4. Verifica que el stock en UI coincide con PostgreSQL.

---

## Etapa 5 — Simulación concurrente

Con la API arriba:

```bash
pip install httpx
python scripts/simulate_orders.py
```

Observa en http://localhost:5173 cómo los tres subscribers registran eventos casi en paralelo.

---

## Observabilidad

- **Prometheus** scrapea `api:8000/metrics`.
- En Grafana (http://localhost:3000) puedes crear un panel con `api_requests_total` o exportar contadores custom que agregues en `analytics_subscriber.py`.

---

## Checklist de entrega sugerido

- [ ] Informe Etapa 1 con benchmark antes/después
- [ ] Caché Redis en categorías, populares y ofertas documentado
- [ ] Invalidación probada con PATCH de stock
- [ ] Subscribers con lógica propia (no solo el `push_event_log` base)
- [ ] Simulación concurrente ejecutada y capturas del feed Pub/Sub
- [ ] (Opcional) Dashboard Grafana con latencia o hit rate de caché

---

## Preguntas frecuentes

**¿Por qué la primera carga es lenta?**  
Es intencional: simula PostgreSQL lento en MISS. La segunda debería ser rápida (HIT).

**¿Los subscribers no aparecen?**  
Revisa `docker compose ps` — deben estar `worker-inventory`, `worker-email`, `worker-analytics`.

**¿Cambié `init.sql` y no veo datos nuevos?**  
El SQL solo corre en la primera creación del volumen. Borra el volumen: `docker compose down -v`.

**¿Dónde no debería gastar tiempo?**  
`main.py`, Docker base y el layout general ya están listos. Enfócate en caché, invalidación y subscribers.

---

¡Éxito en el taller! Si tu docente pide extensiones (rate limiting, JWT, etc.), usa los mismos puntos de extensión: routers + `cache.py` + subscribers.
