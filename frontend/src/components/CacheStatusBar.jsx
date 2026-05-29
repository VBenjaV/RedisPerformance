export default function CacheStatusBar({ cacheTags }) {
  const entries = [
    { key: 'categories', label: 'Categorías' },
    { key: 'products', label: 'Productos' },
    { key: 'offers', label: 'Ofertas' },
  ]

  const hits = entries.filter((e) => cacheTags[e.key] === 'HIT').length
  const defined = entries.filter((e) => cacheTags[e.key]).length

  return (
    <div className="cache-status-bar" role="status" aria-label="Estado de caché Redis">
      <div className="cache-status-bar__left">
        <span className="cache-status-bar__dot" aria-hidden="true" />
        <span>
          Redis · <strong>{hits}</strong>/{defined || '—'} HIT en última carga
        </span>
      </div>
      <div className="cache-status-bar__tags">
        {entries.map(({ key, label }) =>
          cacheTags[key] ? (
            <span key={key} className={`cache-tag ${cacheTags[key] === 'HIT' ? 'hit' : 'miss'}`}>
              {label} {cacheTags[key]}
            </span>
          ) : null,
        )}
      </div>
    </div>
  )
}
