import ProductCard from './ProductCard'

export default function ProductGrid({ products, onAdd, onQuickView }) {
  if (products.length === 0) {
    return (
      <div className="empty-state">
        <span className="empty-state__icon" aria-hidden="true">🔍</span>
        <h3>Sin resultados</h3>
        <p>Prueba otra búsqueda o cambia el filtro de categoría.</p>
      </div>
    )
  }

  return (
    <div className="product-grid">
      {products.map((p) => (
        <ProductCard
          key={p.id}
          product={p}
          onAdd={onAdd}
          onQuickView={onQuickView}
        />
      ))}
    </div>
  )
}
