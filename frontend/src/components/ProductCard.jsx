import { priceFmt } from '../utils/format'

export default function ProductCard({ product, onAdd, onQuickView }) {
  const outOfStock = product.stock <= 0
  const lowStock = product.stock > 0 && product.stock <= 5

  return (
    <article className="product-card">
      <div className="product-card__media">
        <img
          src={product.image_url}
          alt={product.name}
          width={600}
          height={450}
          loading="lazy"
        />
        {product.is_popular && (
          <span className="product-badge product-badge--popular">Popular</span>
        )}
        {lowStock && !outOfStock && (
          <span className="product-badge product-badge--low">Últimas unidades</span>
        )}
        <button
          type="button"
          className="quick-view-btn"
          onClick={() => onQuickView(product)}
          aria-label={`Ver detalle de ${product.name}`}
        >
          Ver detalle
        </button>
      </div>
      <div className="product-body">
        <p className="product-meta">{product.category_name}</p>
        <h3>{product.name}</h3>
        <p className="product-desc">{product.description}</p>
        <div className="product-footer">
          <p className="product-price">{priceFmt.format(product.price)}</p>
          {outOfStock ? (
            <span className="stock-out">Agotado</span>
          ) : (
            <span className="product-meta stock-ok">{product.stock} en stock</span>
          )}
        </div>
        <button
          type="button"
          className="add-btn"
          disabled={outOfStock}
          onClick={() => onAdd(product)}
        >
          {outOfStock ? 'Sin stock' : 'Agregar al carrito'}
        </button>
      </div>
    </article>
  )
}
