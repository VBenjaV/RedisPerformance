import { useEffect } from 'react'
import { priceFmt } from '../utils/format'

export default function ProductDetailModal({ product, onClose, onAdd }) {
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose()
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = ''
    }
  }, [onClose])

  if (!product) return null

  const outOfStock = product.stock <= 0

  return (
    <div className="modal-overlay" onClick={onClose} role="presentation">
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        <button type="button" className="modal-close" onClick={onClose} aria-label="Cerrar">
          ×
        </button>
        <div className="modal-grid">
          <div className="modal-image">
            <img src={product.image_url} alt={product.name} width={800} height={600} />
          </div>
          <div className="modal-content">
            <p className="product-meta">{product.category_name}</p>
            <h2 id="modal-title">{product.name}</h2>
            <p className="modal-desc">{product.description}</p>
            <p className="modal-price">{priceFmt.format(product.price)}</p>
            <dl className="modal-specs">
              <div>
                <dt>Stock disponible</dt>
                <dd>{product.stock} unidades</dd>
              </div>
              <div>
                <dt>ID producto</dt>
                <dd>#{product.id}</dd>
              </div>
            </dl>
            <button
              type="button"
              className="add-btn add-btn--large"
              disabled={outOfStock}
              onClick={() => {
                onAdd(product)
                onClose()
              }}
            >
              {outOfStock ? 'Producto agotado' : 'Agregar al carrito'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
