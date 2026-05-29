import { priceFmt } from '../utils/format'

export default function CartPanel({
  cart,
  total,
  email,
  onEmailChange,
  onCheckout,
  checkingOut,
  onUpdateQty,
  onRemove,
  idPrefix = '',
}) {
  const emailId = `${idPrefix}checkout-email`

  return (
    <div className="panel checkout-form">
      <div className="panel-header">
        <h2>Tu carrito</h2>
        {cart.length > 0 && (
          <span className="panel-badge">{cart.length} ítems</span>
        )}
      </div>

      {cart.length === 0 ? (
        <div className="empty-cart">
          <span className="empty-cart__icon" aria-hidden="true">🛒</span>
          <p>Tu carrito está vacío</p>
          <span className="empty-cart__hint">
            Agrega productos y confirma una orden para ver Pub/Sub en acción.
          </span>
        </div>
      ) : (
        <>
          <ul className="cart-list">
            {cart.map((item) => (
              <li key={item.id} className="cart-item">
                {item.image_url && (
                  <img
                    src={item.image_url}
                    alt=""
                    width={56}
                    height={56}
                    className="cart-item__thumb"
                  />
                )}
                <div className="cart-item__info">
                  <span className="cart-item__name">{item.name}</span>
                  <span className="cart-item__price">{priceFmt.format(item.price)}</span>
                  <div className="qty-controls">
                    <button
                      type="button"
                      className="qty-btn"
                      aria-label={`Disminuir cantidad de ${item.name}`}
                      onClick={() => onUpdateQty(item.id, item.qty - 1)}
                    >
                      −
                    </button>
                    <span className="qty-value">{item.qty}</span>
                    <button
                      type="button"
                      className="qty-btn"
                      aria-label={`Aumentar cantidad de ${item.name}`}
                      disabled={item.qty >= item.stock}
                      onClick={() => onUpdateQty(item.id, item.qty + 1)}
                    >
                      +
                    </button>
                    <button
                      type="button"
                      className="remove-btn"
                      onClick={() => onRemove(item.id)}
                    >
                      Quitar
                    </button>
                  </div>
                </div>
                <span className="cart-item__total">{priceFmt.format(item.price * item.qty)}</span>
              </li>
            ))}
          </ul>

          <div className="cart-summary">
            <div className="cart-summary__row">
              <span>Subtotal</span>
              <span>{priceFmt.format(total)}</span>
            </div>
            <div className="cart-summary__row cart-summary__row--total">
              <span>Total</span>
              <strong>{priceFmt.format(total)}</strong>
            </div>
          </div>

          <label htmlFor={emailId}>Email del cliente</label>
          <input
            id={emailId}
            name="email"
            type="email"
            autoComplete="email"
            spellCheck={false}
            placeholder="alumno@universidad.cl…"
            value={email}
            onChange={(e) => onEmailChange(e.target.value)}
          />
          <button
            type="button"
            className="checkout-btn"
            disabled={checkingOut || !email}
            onClick={onCheckout}
          >
            {checkingOut ? 'Procesando orden…' : 'Confirmar compra'}
          </button>
        </>
      )}
    </div>
  )
}
