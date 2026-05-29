export default function Hero({ stats, onShopClick }) {
  return (
    <section className="hero">
      <div className="hero__content">
        <span className="hero__eyebrow">Semana 11 · Taller evaluado</span>
        <h1>Compra inteligente con arquitectura distribuida</h1>
        <p>
          Catálogo acelerado con Redis, órdenes desacopladas vía Pub/Sub y métricas en
          Prometheus. Ideal para medir latencia antes y después del caché.
        </p>
        <div className="hero__actions">
          <button type="button" className="btn-primary" onClick={onShopClick}>
            Explorar catálogo
          </button>
          <a
            className="btn-ghost"
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
          >
            Ver API Docs
          </a>
        </div>
        <div className="hero-stats">
          <div className="stat-card">
            <strong>{stats.products}</strong>
            <span>Productos</span>
          </div>
          <div className="stat-card">
            <strong>{stats.categories}</strong>
            <span>Categorías</span>
          </div>
          <div className="stat-card">
            <strong>{stats.offers}</strong>
            <span>Ofertas</span>
          </div>
        </div>
      </div>
      <div className="hero-visual">
        <img
          src="https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=900"
          alt="Compras en línea con tarjeta y laptop"
          width={900}
          height={675}
          loading="eager"
        />
        <div className="hero-visual__card">
          <span>Latencia objetivo</span>
          <strong>480ms → 15ms</strong>
          <small>Con caché Redis (Etapa 2)</small>
        </div>
      </div>
    </section>
  )
}
