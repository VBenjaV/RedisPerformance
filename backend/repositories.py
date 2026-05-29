from db.connection import get_connection


def fetch_categories():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, slug FROM categories ORDER BY name")
            return [dict(row) for row in cur.fetchall()]


def fetch_products(category_id: int | None = None, popular_only: bool = False):
    query = """
        SELECT p.id, p.category_id, c.name AS category_name, p.name, p.description,
               p.price::float, p.stock, p.image_url, p.is_popular
        FROM products p
        JOIN categories c ON c.id = p.category_id
        WHERE 1=1
    """
    params: list = []
    if category_id:
        query += " AND p.category_id = %s"
        params.append(category_id)
    if popular_only:
        query += " AND p.is_popular = TRUE"
    query += " ORDER BY p.is_popular DESC, p.name"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]


def fetch_product(product_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.id, p.category_id, c.name AS category_name, p.name, p.description,
                       p.price::float, p.stock, p.image_url, p.is_popular
                FROM products p
                JOIN categories c ON c.id = p.category_id
                WHERE p.id = %s
                """,
                (product_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None


def fetch_offers():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT o.id, o.title, o.discount_percent, o.product_id, o.active,
                       p.name AS product_name, p.price::float AS product_price
                FROM offers o
                JOIN products p ON p.id = o.product_id
                WHERE o.active = TRUE
                ORDER BY o.discount_percent DESC
                """
            )
            return [dict(row) for row in cur.fetchall()]


def create_order(customer_email: str, items: list[dict]) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            total = 0.0
            resolved = []
            for item in items:
                cur.execute(
                    "SELECT id, name, price::float, stock, category_id FROM products WHERE id = %s",
                    (item["product_id"],),
                )
                product = cur.fetchone()
                if not product:
                    raise ValueError(f"Producto {item['product_id']} no existe")
                qty = item["quantity"]
                if product["stock"] < qty:
                    raise ValueError(f"Stock insuficiente para {product['name']}")
                line_total = float(product["price"]) * qty
                total += line_total
                resolved.append({**dict(product), "quantity": qty, "line_total": line_total})

            cur.execute(
                "INSERT INTO orders (customer_email, status, total) VALUES (%s, %s, %s) RETURNING id, created_at",
                (customer_email, "pending", total),
            )
            order = dict(cur.fetchone())
            order_id = order["id"]

            for line in resolved:
                cur.execute(
                    """
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, line["id"], line["quantity"], line["price"]),
                )
                cur.execute(
                    "UPDATE products SET stock = stock - %s WHERE id = %s",
                    (line["quantity"], line["id"]),
                )

            conn.commit()
            return {
                "order_id": order_id,
                "customer_email": customer_email,
                "total": total,
                "items": resolved,
                "created_at": str(order["created_at"]),
            }


def update_product_stock(product_id: int, stock: int) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE products SET stock = %s
                WHERE id = %s
                RETURNING id, category_id, name, stock
                """,
                (stock, product_id),
            )
            row = cur.fetchone()
            conn.commit()
            return dict(row) if row else None
