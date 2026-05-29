export default function SkeletonGrid({ count = 6 }) {
  return (
    <div className="product-grid" aria-busy="true" aria-label="Cargando productos">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton-card">
          <div className="skeleton skeleton-img" />
          <div className="skeleton-body">
            <div className="skeleton skeleton-line w-40" />
            <div className="skeleton skeleton-line w-80" />
            <div className="skeleton skeleton-line w-60" />
            <div className="skeleton skeleton-btn" />
          </div>
        </div>
      ))}
    </div>
  )
}
