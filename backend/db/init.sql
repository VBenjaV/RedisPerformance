CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    slug VARCHAR(120) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    image_url TEXT,
    is_popular BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS offers (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    discount_percent INTEGER NOT NULL,
    product_id INTEGER REFERENCES products(id),
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_email VARCHAR(200) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    total NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL
);

INSERT INTO categories (name, slug) VALUES
    ('Tecnología', 'tecnologia'),
    ('Hogar', 'hogar'),
    ('Deportes', 'deportes');

INSERT INTO products (category_id, name, description, price, stock, image_url, is_popular) VALUES
    (1, 'Laptop Pro 14"', 'Ultrabook para desarrollo y diseño.', 1299.99, 12, 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600', TRUE),
    (1, 'Mouse ergonómico', 'Sensor de alta precisión y batería de larga duración.', 49.99, 80, 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600', TRUE),
    (1, 'Teclado mecánico', 'Switches silenciosos y retroiluminación RGB.', 89.99, 35, 'https://images.unsplash.com/photo-1587829741301-d798b0a0e5a0?w=600', FALSE),
    (2, 'Cafetera automática', 'Espresso y cappuccino en un solo equipo.', 199.99, 20, 'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e0?w=600', TRUE),
    (2, 'Aspiradora inteligente', 'Mapeo láser y control desde la app.', 349.99, 8, 'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=600', FALSE),
    (3, 'Bicicleta urbana', 'Cuadro de aluminio y 7 velocidades.', 459.99, 5, 'https://images.unsplash.com/photo-1485965120188-e220f721d03f?w=600', TRUE),
    (3, 'Mochila deportiva', 'Compartimento impermeable para laptop.', 59.99, 45, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600', FALSE);

INSERT INTO products (id, category_id, name, description, price, stock, image_url, is_popular) VALUES
    (15, 1, 'Producto benchmark #15', 'Endpoint de referencia para ab -n 1000 -c 100 /productos/15', 99.99, 100,
     'https://images.unsplash.com/photo-1505744386214-5093af9ab0cf?w=600', TRUE);

SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));

INSERT INTO offers (title, discount_percent, product_id, active) VALUES
    ('Hot Sale Laptop', 15, 1, TRUE),
    ('Combo oficina', 10, 2, TRUE),
    ('Fin de semana deportivo', 20, 6, TRUE);
