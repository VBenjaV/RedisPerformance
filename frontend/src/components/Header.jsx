export default function Header({ cartCount, onOpenCart, search, onSearchChange }) {
  return (
    <header className="site-header">
      <div className="header-brand">
        <div className="logo">
          <span className="logo-mark" aria-hidden="true">
            S
          </span>
          <div>
            <span className="logo-text" translate="no">
              ShopNow
            </span>
            <span className="logo-sub">Backend distribuido</span>
          </div>
        </div>
      </div>

      <div className="header-search">
        <label htmlFor="header-search" className="visually-hidden">
          Buscar en la tienda
        </label>
        <input
          id="header-search"
          type="search"
          name="header-q"
          placeholder="Buscar productos…"
          autoComplete="off"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      <nav className="header-nav" aria-label="Enlaces útiles">
        <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
          API
        </a>
        <a href="http://localhost:9090" target="_blank" rel="noreferrer">
          Prometheus
        </a>
        <a href="http://localhost:3000" target="_blank" rel="noreferrer">
          Grafana
        </a>
      </nav>

      <div className="header-actions">
        <button
          type="button"
          className="cart-btn"
          onClick={onOpenCart}
          aria-label={`Abrir carrito, ${cartCount} artículos`}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49A1 1 0 0 0 20 5H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z"
            />
          </svg>
          <span>Carrito</span>
          {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
        </button>
      </div>
    </header>
  )
}
