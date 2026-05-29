export default function Footer() {
  return (
    <footer className="site-footer">
      <p>
        <span translate="no">ShopNow</span> — Plantilla taller backend distribuido
      </p>
      <nav aria-label="Recursos del taller">
        <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
          Swagger
        </a>
        <a href="http://localhost:9090" target="_blank" rel="noreferrer">
          Prometheus
        </a>
        <a href="http://localhost:3000" target="_blank" rel="noreferrer">
          Grafana
        </a>
      </nav>
      <p className="site-footer__hint">Edita el frontend en <code>frontend/src/</code></p>
    </footer>
  )
}
