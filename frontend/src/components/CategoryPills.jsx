export default function CategoryPills({ categories, activeId, onSelect, loading }) {
  return (
    <div className="category-section">
      <div className="section-title">
        <h2 className="section-heading" id="catalogo">
          Catálogo
        </h2>
      </div>
      <div className="category-pills" role="tablist" aria-label="Filtrar por categoría">
        <button
          type="button"
          role="tab"
          className={`pill ${activeId === null ? 'active' : ''}`}
          onClick={() => onSelect(null)}
          aria-selected={activeId === null}
          disabled={loading}
        >
          Todos
        </button>
        <button
          type="button"
          role="tab"
          className={`pill ${activeId === 'popular' ? 'active' : ''}`}
          onClick={() => onSelect('popular')}
          aria-selected={activeId === 'popular'}
          disabled={loading}
        >
          ⭐ Populares
        </button>
        {categories.map((cat) => (
          <button
            key={cat.id}
            type="button"
            role="tab"
            className={`pill ${activeId === cat.id ? 'active' : ''}`}
            onClick={() => onSelect(cat.id)}
            aria-selected={activeId === cat.id}
            disabled={loading}
          >
            {cat.name}
          </button>
        ))}
      </div>
    </div>
  )
}
