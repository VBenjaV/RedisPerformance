export default function SearchSortBar({ search, onSearchChange, sort, onSortChange, resultCount, loading }) {
  return (
    <div className="search-sort-bar">
      <div className="search-wrap">
        <label htmlFor="product-search" className="visually-hidden">
          Buscar productos
        </label>
        <svg className="search-icon" width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
          <path
            fill="currentColor"
            d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"
          />
        </svg>
        <input
          id="product-search"
          type="search"
          name="q"
          placeholder="Buscar laptop, hogar, deportes…"
          autoComplete="off"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>
      <div className="search-sort-bar__right">
        <span className="result-count" aria-live="polite">
          {loading ? 'Actualizando…' : `${resultCount} productos`}
        </span>
        <label htmlFor="sort-select" className="visually-hidden">
          Ordenar productos
        </label>
        <select
          id="sort-select"
          name="sort"
          className="sort-select"
          value={sort}
          onChange={(e) => onSortChange(e.target.value)}
        >
          <option value="featured">Destacados</option>
          <option value="price-asc">Precio: menor a mayor</option>
          <option value="price-desc">Precio: mayor a menor</option>
          <option value="stock">Mayor stock</option>
        </select>
      </div>
    </div>
  )
}
